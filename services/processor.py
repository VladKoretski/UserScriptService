import logging
import time
from config.settings import get_config
from llm.prompt_builder import build_prompt
from llm.client import call_llm
from cache.ttl_cache import TTLCache

logger = logging.getLogger(__name__)
cache = TTLCache(ttl=get_config()["CACHE_TTL"])

def post_process(raw_text: str) -> str:
    cleaned = raw_text.strip().replace("```", "").strip()
    return cleaned if cleaned else "No response generated."

def process_request(query: str) -> dict:
    t0 = time.time()
    logger.info(f"PIPELINE_START: query_len={len(query)}")

    cfg = get_config()
    sys_prompt, user_msg = build_prompt(query)

    # 1. Проверка кеша
    cached = cache.get(user_msg, cfg["LLM_MODEL"], cfg["LLM_TEMPERATURE"], sys_prompt)
    if cached:
        logger.info(f"PIPELINE_END: cache_hit latency={round(time.time()-t0, 3)}s")
        return {"response": cached, "source": "cache", "latency": round(time.time()-t0, 3)}

    # 2. Формирование запроса
    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_msg}]

    # 3. Вызов LLM с fallback
    try:
        raw_response = call_llm(messages)
    except Exception as e:
        logger.error(f"LLM_CALL_FAILED: {e}")
        return {"response": "Service temporarily unavailable. Please try again later.", "source": "fallback", "latency": round(time.time()-t0, 3)}

    # 4. Пост-обработка
    final_response = post_process(raw_response)

    # 5. Сохранение в кеш
    cache.set(user_msg, cfg["LLM_MODEL"], cfg["LLM_TEMPERATURE"], sys_prompt, final_response)

    logger.info(f"PIPELINE_END: latency={round(time.time()-t0, 3)}s")
    return {"response": final_response, "source": "llm", "latency": round(time.time()-t0, 3)}