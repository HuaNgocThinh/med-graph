"""
LLMClient Abstraction Layer for MedGraph-VI.
Supports Gemini (via google-genai SDK or legacy google.generativeai), OpenAI, Anthropic, and a fallback Mock provider.
Includes dynamic model discovery, active rate limiting (GEMINI_RPM_LIMIT), daily RPD usage tracking,
error classification (FATAL_AUTH, FATAL_BILLING, RETRYABLE), and execution statistics tracking.
"""

import os
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union, List
from src.config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL_NAME, DATA_DIR, BASE_DIR, GEMINI_MODEL_FALLBACK_LIST

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LLMClient")

# Usage tracker file path
USAGE_TRACKER_PATH = DATA_DIR / ".api_usage_tracker.json"


class FatalQuotaZeroError(Exception):
    """Raised when a model returns RESOURCE_EXHAUSTED with limit: 0 (no free tier available for this model)."""
    pass


def classify_api_error(e: Exception) -> str:
    """
    Classifies API errors into categories:
    - 'FATAL_AUTH': Bad API key, permission denied (HTTP 400/401/403)
    - 'FATAL_BILLING': Billing disabled/inactive
    - 'FATAL_QUOTA_ZERO': RESOURCE_EXHAUSTED with limit: 0 or quotaValue: 0 (No Free Tier for this model, non-retryable)
    - 'RETRYABLE': Rate limit hit (HTTP 429 / RESOURCE_EXHAUSTED with limit > 0)
    - 'OTHER': Non-429 server error / model error
    """
    err_msg = str(e)
    code = getattr(e, "code", None) or getattr(e, "status_code", None)
    err_msg_lower = err_msg.lower()

    is_fatal_auth = any(token in err_msg_lower for token in [
        "api_key_invalid", "api key not valid", "invalid api key", "unauthenticated", "permission_denied"
    ]) or (code in (400, 401, 403) and any(k in err_msg_lower for k in ["key", "auth", "permission"]))

    if is_fatal_auth:
        return "FATAL_AUTH"

    is_fatal_billing = any(token in err_msg_lower for token in [
        "billing_disabled", "billing has not been enabled", "account_disabled", "pay-as-you-go"
    ])

    if is_fatal_billing:
        return "FATAL_BILLING"

    is_quota_or_exhausted = (
        code == 429
        or "429" in err_msg
        or "resource_exhausted" in err_msg_lower
        or "quota" in err_msg_lower
        or "rate limit" in err_msg_lower
    )

    if is_quota_or_exhausted:
        if re.search(r"(?:limit|quotavalue|quota_value)['\"\s:]+0\b", err_msg_lower):
            return "FATAL_QUOTA_ZERO"
        return "RETRYABLE"

    return "OTHER"


def update_env_model_name(new_model: str):
    """Updates LLM_MODEL_NAME in .env file to persist the working model across runs."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        logger.warning(f".env file not found at {env_path}. Creating new .env file.")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"LLM_MODEL_NAME={new_model}\n")
        os.environ["LLM_MODEL_NAME"] = new_model
        return

    try:
        content = env_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        updated = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("LLM_MODEL_NAME="):
                new_lines.append(f"LLM_MODEL_NAME={new_model}")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"LLM_MODEL_NAME={new_model}")

        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        os.environ["LLM_MODEL_NAME"] = new_model
        logger.info(f"💾 Updated .env file: LLM_MODEL_NAME='{new_model}'")
    except Exception as e:
        logger.error(f"Failed to update .env file: {e}")


class LLMClient:
    """Multi-provider LLM client with rate limiting, daily quota tracking, error handling, and mock fallback."""

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.provider = (provider or os.getenv("LLM_PROVIDER") or LLM_PROVIDER).lower()

        if self.provider == "gemini":
            self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY") or LLM_API_KEY
        elif self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY") or LLM_API_KEY
        elif self.provider == "anthropic":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("LLM_API_KEY") or LLM_API_KEY
        else:
            self.api_key = api_key or LLM_API_KEY

        self.model_name = os.getenv("GEMINI_MODEL") or model_name or LLM_MODEL_NAME

        # Client-side Active Rate Limiter (RPM)
        # Default for gemini-2.5-flash-lite Free Tier is ~15 RPM, default limit to 10 RPM (6.0s delay) for safe buffer
        self.rpm_limit = float(os.getenv("GEMINI_RPM_LIMIT", "10"))
        self.min_request_interval = 60.0 / self.rpm_limit if self.rpm_limit > 0 else 0.0

        if not self.api_key and self.provider != "mock":
            logger.warning(f"No API key provided for '{self.provider}'. Falling back to 'mock' mode.")
            self.provider = "mock"

        self._validated = False
        self._last_request_time = 0.0
        self.real_calls_count = 0
        self.mock_calls_count = 0
        self.is_mock_fallback = (self.provider == "mock")
        self.corrupted_json_count = 0
        self.total_json_attempts = 0

        logger.info(f"Initialized LLMClient with provider='{self.provider}', model='{self.model_name}', rpm_limit={self.rpm_limit:.0f} RPM")

    def list_available_models(self) -> List[str]:
        """
        Lists available generative models for the active API key using modern google-genai SDK.
        Strips 'models/' prefix and filters for text generative models.
        """
        if self.provider != "gemini" or not self.api_key:
            return []

        models = []
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            for m in client.models.list():
                name = getattr(m, "name", str(m))
                if name.startswith("models/"):
                    name = name[7:]

                name_lower = name.lower()
                if "gemini" in name_lower or "flash" in name_lower or "pro" in name_lower:
                    if not any(excluded in name_lower for excluded in ["embedding", "aqa", "imagen", "bidi", "tts", "stt", "computer-use"]):
                        models.append(name)
        except Exception as e1:
            logger.debug(f"google-genai client.models.list() call failed: {e1}")
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=self.api_key)
                for m in genai_legacy.list_models():
                    methods = getattr(m, "supported_generation_methods", [])
                    if "generateContent" in methods:
                        name = m.name.replace("models/", "")
                        models.append(name)
            except Exception as e2:
                logger.error(f"Could not retrieve Gemini model list: {e1} / {e2}")
                raise e1

        return models

    def select_best_model(self, available_models: List[str]) -> str:
        """
        Selects the optimal lightweight/flash model from available models.
        Supports override via GEMINI_MODEL env var or configured self.model_name.
        """
        env_override = os.getenv("GEMINI_MODEL")
        if env_override:
            clean_override = env_override.replace("models/", "").strip()
            logger.info(f"Using GEMINI_MODEL override from environment: '{clean_override}'")
            return clean_override

        if not available_models:
            return self.model_name

        # Priority 0: Check if self.model_name is explicitly set in config/.env and available
        if self.model_name:
            clean_model = self.model_name.replace("models/", "").strip()
            for m in available_models:
                if clean_model.lower() == m.lower():
                    logger.info(f"Using configured model name: '{m}'")
                    return m

        # Priority 1: Flash-Lite 2.5/1.5 models (lightweight, higher quota)
        for m in available_models:
            m_lower = m.lower()
            if "2.5-flash-lite" in m_lower or "1.5-flash-lite" in m_lower:
                return m

        for m in available_models:
            m_lower = m.lower()
            if "flash" in m_lower and "lite" in m_lower:
                return m

        # Priority 2: Stable Flash models
        for m in available_models:
            m_lower = m.lower()
            if "flash" in m_lower and "exp" not in m_lower and "preview" not in m_lower:
                return m

        # Priority 3: Any Flash model
        for m in available_models:
            if "flash" in m.lower():
                return m

        # Priority 4: Pro or standard models
        for m in available_models:
            m_lower = m.lower()
            if "pro" in m_lower or "gemini" in m_lower:
                return m

        return available_models[0]

    def validate_connection(self) -> bool:
        """
        Validates LLM API connection.
        Lists available models (logged once), selects best model, and executes a test prompt.
        If validation fails due to FATAL_QUOTA_ZERO (limit: 0), automatically probes models in fallback list.
        """
        if self._validated:
            return True

        if self.provider == "mock":
            logger.info("Operating in 'mock' mode (offline simulation).")
            self._validated = True
            return True

        logger.info(f"🔍 Validating connection to {self.provider.upper()} API...")

        # 1. Discover available models if Gemini
        if self.provider == "gemini":
            try:
                avail_models = self.list_available_models()
                if avail_models:
                    logger.info(f"📋 Available Gemini models for API key ({len(avail_models)}): {avail_models}")
                    selected = self.select_best_model(avail_models)
                    logger.info(f"🎯 Auto-selected Gemini model: '{selected}'")
                    self.model_name = selected
                else:
                    logger.warning("No Gemini models returned from API listing. Retaining default model name.")
            except Exception as e:
                err_type = classify_api_error(e)
                if err_type == "FATAL_QUOTA_ZERO":
                    logger.warning(f"⚠️ Model listing hit limit: 0: {e}")
                else:
                    logger.error(f"❌ {self.provider.title()} API connection FAILED during model listing: {e}")
                    self._validated = False
                    return False

        # 2. Execute test ping prompt with fallback support
        test_prompt = "Xin chào, vui lòng phản hồi 'OK'."

        # Build prioritized candidate queue: current model_name first, then GEMINI_MODEL_FALLBACK_LIST items
        candidate_models = [self.model_name]
        for m in GEMINI_MODEL_FALLBACK_LIST:
            if m not in candidate_models:
                candidate_models.append(m)

        initial_model = self.model_name
        last_failed_model = None

        for model in candidate_models:
            try:
                self.model_name = model
                resp = self._execute_real_api_call(test_prompt, system_prompt=None, temperature=0.1)
                if resp and len(resp) > 0:
                    if model != initial_model:
                        failed_name = last_failed_model or initial_model
                        logger.warning(f"⚠️ Model '{failed_name}' không có free tier, tự động chuyển sang '{model}'")
                        update_env_model_name(model)
                    logger.info(f"✅ {self.provider.title()} API connected successfully (Model: {self.model_name})")
                    self._validated = True
                    return True
                else:
                    raise ValueError("Empty response received from LLM test prompt.")
            except FatalQuotaZeroError as e:
                last_failed_model = model
                logger.warning(f"⚠️ Model '{model}' không có free tier (limit: 0). Thử model tiếp theo trong danh sách dự phòng...")
                continue
            except Exception as e:
                err_type = classify_api_error(e)
                if err_type in ("FATAL_AUTH", "FATAL_BILLING"):
                    logger.error(f"❌ {self.provider.title()} API connection FAILED: {e}")
                    self._validated = False
                    return False

                last_failed_model = model
                logger.warning(f"⚠️ Model '{model}' không khả dụng hoặc gặp lỗi ({e}). Thử model tiếp theo trong danh sách dự phòng...")
                continue

        logger.error(f"❌ Tất cả các model trong danh sách dự phòng ({candidate_models}) đều thất bại!")
        self._validated = False
        return False

    def _show_mock_banner(self, reason: str = ""):
        if not self.is_mock_fallback:
            self.is_mock_fallback = True
            logger.warning("=" * 70)
            logger.warning(f"⚠️ SIMULATED_OFFLINE: LLM provider '{self.provider}' fell back to MOCK mode! ({reason})")
            logger.warning("======================================================================")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Sends prompt to configured LLM provider with rate limiting and retry logic."""
        if self.provider == "mock":
            self.is_mock_fallback = True
            self.mock_calls_count += 1
            return self._call_mock(prompt, system_prompt)

        try:
            result = self._execute_real_api_call(prompt, system_prompt=system_prompt, temperature=temperature)
            self.real_calls_count += 1
            return result
        except Exception as e:
            self._show_mock_banner(reason=str(e))
            logger.error(f"LLM API call failed: {e}. Falling back to mock response.")
            self.mock_calls_count += 1
            return self._call_mock(prompt, system_prompt)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Union[Dict[str, Any], list]:
        """Generates text and parses extracted JSON output."""
        self.total_json_attempts += 1
        raw_response = self.generate(prompt, system_prompt=system_prompt, temperature=0.1)
        res = self._extract_json(raw_response)

        # Mark output with source: mock if generated in mock fallback or mock mode
        if self.is_mock_fallback or self.provider == "mock":
            if isinstance(res, list):
                for item in res:
                    if isinstance(item, dict):
                        item["source"] = "mock"
            elif isinstance(res, dict):
                res["source"] = "mock"

        return res

    def _track_daily_usage(self):
        """Tracks daily API call count and warns if approaching RPD quota threshold (80%)."""
        try:
            utc_now = datetime.now(timezone.utc)
            # Google daily quota resets at Midnight Pacific Time = 08:00 UTC
            quota_day = (utc_now - timedelta(hours=8)).strftime("%Y-%m-%d")

            usage_data = {}
            if USAGE_TRACKER_PATH.exists():
                try:
                    with open(USAGE_TRACKER_PATH, "r", encoding="utf-8") as f:
                        usage_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Error reading usage tracker at '{USAGE_TRACKER_PATH}': {e}")
                    usage_data = {}

            current_count = usage_data.get(quota_day, 0) + 1
            usage_data[quota_day] = current_count

            with open(USAGE_TRACKER_PATH, "w", encoding="utf-8") as f:
                json.dump(usage_data, f, ensure_ascii=False, indent=2)

            rpd_limit = int(os.getenv("GEMINI_RPD_LIMIT", "1000"))
            threshold = int(0.8 * rpd_limit)
            if current_count >= threshold:
                logger.warning(
                    f"⚠️ Đã dùng {current_count}/{rpd_limit} request hôm nay ({current_count/rpd_limit*100:.1f}%), "
                    f"gần chạm giới hạn Free Tier. Cân nhắc dừng lại hoặc đợi reset (UTC 08:00)."
                )
        except Exception as e:
            logger.debug(f"Usage tracking error: {e}")

    def _execute_real_api_call(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Executes real API call with proactive rate-limiting throttle and 429 exponential backoff retries."""
        # Active Rate Limiter Throttle (based on GEMINI_RPM_LIMIT)
        now = time.time()
        elapsed = now - self._last_request_time
        if self.min_request_interval > 0 and elapsed < self.min_request_interval and self._last_request_time > 0:
            sleep_time = round(self.min_request_interval - elapsed, 2)
            logger.info(f"⏳ Active Rate Limiter: Waiting {sleep_time}s before sending LLM request (Rate limit: {self.rpm_limit:.0f} RPM)...")
            time.sleep(sleep_time)

        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                self._last_request_time = time.time()
                if self.provider == "gemini":
                    res = self._call_gemini_api(prompt, system_prompt, temperature)
                elif self.provider == "openai":
                    res = self._call_openai_api(prompt, system_prompt, temperature)
                elif self.provider == "anthropic":
                    res = self._call_anthropic_api(prompt, system_prompt, temperature)
                else:
                    res = self._call_mock(prompt, system_prompt)

                self._track_daily_usage()
                return res

            except Exception as e:
                last_error = e
                err_msg = str(e)
                err_type = classify_api_error(e)

                if err_type == "FATAL_AUTH":
                    logger.error(f"❌ FATAL AUTH ERROR: {err_msg}")
                    raise last_error

                if err_type == "FATAL_BILLING":
                    logger.error(f"❌ FATAL BILLING ERROR: {err_msg}")
                    raise last_error

                if err_type == "FATAL_QUOTA_ZERO":
                    logger.error(f"❌ FATAL QUOTA ZERO ERROR: Model '{self.model_name}' has limit: 0 for free tier: {err_msg}")
                    raise FatalQuotaZeroError(f"Model '{self.model_name}' has limit: 0 for free tier: {err_msg}")

                if err_type == "RETRYABLE":
                    retry_delay = 12.0 * attempt
                    delay_match = re.search(r"retry(?:_delay| in| after)?[:\s]+(\d+(?:\.\d+)?)s?", err_msg, re.IGNORECASE)
                    delay_match_sec = re.search(r"seconds:\s*(\d+)", err_msg, re.IGNORECASE)
                    delay_match_word = re.search(r"(\d+(?:\.\d+)?)\s*seconds", err_msg, re.IGNORECASE)

                    if delay_match:
                        retry_delay = float(delay_match.group(1)) + 0.5
                    elif delay_match_sec:
                        retry_delay = float(delay_match_sec.group(1)) + 0.5
                    elif delay_match_word:
                        retry_delay = float(delay_match_word.group(1)) + 0.5

                    if attempt < max_retries:
                        logger.warning(f"⏳ Rate limit 429 hit. Waiting {retry_delay:.1f}s before retry ({attempt}/{max_retries})...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"❌ Rate limit 429 persisted after {max_retries} attempts.")
                        raise last_error
                else:
                    # Non-429 error (e.g. 404 model error) - raise immediately without 429 retry
                    raise last_error

        raise last_error or RuntimeError("Unknown API execution failure")


    def _call_gemini_api(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        # Try modern google-genai SDK first
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_prompt if system_prompt else None
            )
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            elif hasattr(response, "candidates") and response.candidates and response.candidates[0].content:
                parts = response.candidates[0].content.parts
                return "".join([p.text for p in parts if hasattr(p, "text")]).strip()
            else:
                raise ValueError(f"Gemini API returned empty response: {response}")
        except Exception as e:
            if "google.genai" in sys.modules or "genai" in locals():
                raise e

            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=self.api_key)
                model = genai_legacy.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_prompt if system_prompt else None
                )
                response = model.generate_content(
                    prompt,
                    generation_config=genai_legacy.types.GenerationConfig(temperature=temperature)
                )
                return response.text.strip()
            except Exception:
                raise e

    def _call_openai_api(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model_name if "gpt" in self.model_name else "gpt-3.5-turbo",
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    def _call_anthropic_api(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model_name if "claude" in self.model_name else "claude-3-haiku-20240307",
            max_tokens=1500,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.content[0].text.strip()

    def _call_mock(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Mock generator for offline testing and hardware-constrained CPU environments."""
        prompt_lower = prompt.lower()
        sys_lower = (system_prompt or "").lower()

        if "cypher" in prompt_lower or "neo4j" in prompt_lower or "câu lệnh cypher" in prompt_lower or "cypher query" in sys_lower:
            if "chống chỉ định" in prompt_lower:
                if "dạ dày" in prompt_lower:
                    return "MATCH (d:DRUG)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'dạ dày' RETURN d.name AS ThuocChongChiDinh, b.name AS Benh"
                return "MATCH (d:DRUG)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) RETURN d.name AS ThuocChongChiDinh, b.name AS Benh"
            elif "thuốc" in prompt_lower or "kê" in prompt_lower or "điều trị" in prompt_lower:
                if "dạ dày" in prompt_lower:
                    return "MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'dạ dày' RETURN d.name AS Thuoc, b.name AS Benh"
                elif "huyết áp" in prompt_lower:
                    return "MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'huyết áp' RETURN d.name AS Thuoc, b.name AS Benh"
                return "MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'Đái tháo đường' RETURN d.name AS Thuoc, type(r) AS QuanHe, b.name AS Benh"
            return "MATCH (head)-[r]->(tail) RETURN head.name, type(r), tail.name LIMIT 10"

        elif "sinh" in prompt_lower or "synthetic" in prompt_lower or "bệnh án" in prompt_lower:
            return json.dumps([
                {
                    "id": "syn_001",
                    "template_type": "nội khoa",
                    "text": "Bệnh nhân nam 54 tuổi, có tiền sử Đái tháo đường týp 2 và Cao huyết áp 3 năm nay. Hiện tại ho kéo dài và khó thở. Khám không thấy dấu hiệu Viêm phổi. Bệnh nhân được kê Paracetamol 500mg và Metformin."
                },
                {
                    "id": "syn_002",
                    "template_type": "ngoại khoa",
                    "text": "Bệnh nhân nữ 42 tuổi, nhập viện vì Cơn đau thắt ngực cấp tính. Tiền sử chưa ghi nhận Bệnh Gút. Bác sĩ chỉ định Aspirin 81mg và Atorvastatin để điều trị."
                },
                {
                    "id": "syn_003",
                    "template_type": "kê đơn thuốc",
                    "text": "Bệnh nhân Viêm loét dạ dày kèm trào ngược dạ dày. Không phát hiện Tiêu chảy cấp. Chống chỉ định với Ibuprofen. Đã kê Omeprazole 20mg."
                }
            ], ensure_ascii=False, indent=2)

        elif "relation" in prompt_lower or "quan hệ" in prompt_lower or "triple" in sys_lower or "bộ ba" in prompt_lower:
            entities_in_prompt = []
            for match in re.finditer(r"'([^']+)'\s*\((DISEASE|DRUG|SYMPTOM|PROCEDURE|DRUG_GROUP)\)", prompt):
                entities_in_prompt.append({"entity": match.group(1), "type": match.group(2)})

            triples = []
            drugs = [e["entity"] for e in entities_in_prompt if e["type"] in ("DRUG", "DRUG_GROUP")]
            diseases = [e["entity"] for e in entities_in_prompt if e["type"] == "DISEASE"]
            symptoms = [e["entity"] for e in entities_in_prompt if e["type"] == "SYMPTOM"]

            for drug in drugs:
                for dis in diseases:
                    triples.append({"head": drug, "relation": "PRESCRIBED_FOR", "tail": dis, "confidence": 0.95, "evidence_span": f"kê {drug} cho {dis}"})
                for sym in symptoms:
                    triples.append({"head": drug, "relation": "TREATS", "tail": sym, "confidence": 0.92, "evidence_span": f"dùng {drug} để điều trị {sym}"})
            for dis in diseases:
                for sym in symptoms:
                    triples.append({"head": dis, "relation": "HAS_SYMPTOM", "tail": sym, "confidence": 0.90, "evidence_span": f"{dis} biểu hiện triệu chứng {sym}"})

            return json.dumps(triples, ensure_ascii=False, indent=2)

        elif "ner" in prompt_lower or "thực thể" in prompt_lower or ("entity" in sys_lower and "cypher" not in sys_lower):
            return json.dumps([
                {"entity": "Đái tháo đường týp 2", "type": "DISEASE", "start": 33, "end": 53},
                {"entity": "Cao huyết áp", "type": "DISEASE", "start": 57, "end": 69},
                {"entity": "Paracetamol 500mg", "type": "DRUG", "start": 135, "end": 152},
                {"entity": "Metformin", "type": "DRUG", "start": 156, "end": 165}
            ], ensure_ascii=False, indent=2)

        else:
            return "Dựa trên Knowledge Graph y tế: Thuốc được chỉ định để điều trị bệnh Đái tháo đường týp 2 là Metformin."

    def get_stats_summary(self) -> str:
        """Returns readable summary of real vs mock LLM calls and corrupted JSON counts."""
        total = self.real_calls_count + self.mock_calls_count
        summary = f"=== LLM CALL STATS: {self.real_calls_count}/{total} calls succeeded via real API, {self.mock_calls_count}/{total} fell back to mock ==="
        if self.corrupted_json_count > 0:
            pct = (self.corrupted_json_count / max(1, self.total_json_attempts)) * 100
            summary += f"\n⚠️ WARNING: {self.corrupted_json_count} triple bị mất do JSON hỏng ({pct:.1f}% của tổng)"
        return summary

    def _extract_json(self, text: str) -> Union[Dict[str, Any], list]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError as e:
                    logger.debug(f"Regex fallback JSON decode failed: {e}")
            self.corrupted_json_count += 1
            pct = (self.corrupted_json_count / max(1, self.total_json_attempts)) * 100
            logger.warning(
                f"⚠️ WARNING: {self.corrupted_json_count} triple bị mất do JSON hỏng "
                f"({pct:.1f}% của tổng {self.total_json_attempts} lần). Raw: {cleaned[:100]}..."
            )
            return []
