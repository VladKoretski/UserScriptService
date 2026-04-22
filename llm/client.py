import time
import requests
import logging
from config.settings import get_config

logger = logging.getLogger(__name__)

def call_llm(messages: list[dict], max_retries: int = 3, base_delay: float = 1.0) -> str:
    cfg = get_config()

    # Режим тестирования без реального API-ключа
    if not cfg["LLM_API_KEY"] or "your_key_here" in cfg["LLM_API_KEY"]:
        logger.warning("TEST MODE: mock response (API key not configured)")
        time.sleep(0.3)
        return "Mock response: LLM service is working. Query received successfully."

    url = cfg["LLM_API_URL"]
    headers = {"Authorization": f"Bearer {cfg['LLM_API_KEY']}", "Content-Type": "application/json"}
    payload = {"model": cfg["LLM_MODEL"], "messages": messages, "temperature": cfg["LLM_TEMPERATURE"]}

    for attempt in range(max_retries):
        try:
            logger.info(f"LLM_CALL: attempt={attempt+1}/{max_retries} url={url}")
            resp = requests.post(url, json=payload, headers=headers, timeout=30)

            if resp.status_code >= 500:
                raise requests.exceptions.HTTPError(f"Server error: {resp.status_code}", response=resp)

            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content or not content.strip():
                raise ValueError("Empty content from LLM")
            return content.strip()

        except requests.exceptions.Timeout:
            logger.warning("LLM_TIMEOUT: exceeded 30s")
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code < 500:
                logger.error(f"LLM_CLIENT_ERROR: {e}")
                raise
            logger.warning(f"LLM_SERVER_ERROR: {e}")
        except Exception as e:
            logger.error(f"LLM_UNEXPECTED: {e}")
            if attempt == max_retries - 1:
                raise

        delay = base_delay * (2 ** attempt)
        logger.info(f"RETRY: sleeping {delay:.1f}s")
        time.sleep(delay)

    raise RuntimeError("LLM_UNREACHABLE after retries")