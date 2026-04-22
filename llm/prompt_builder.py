def build_prompt(query: str, scenario: str = "summarization") -> tuple[str, str]:
    if scenario == "summarization":
        sys_prompt = (
            "Ты — профессиональный редактор. Твоя задача — кратко суммировать предоставленный текст. "
            "Ответ должен быть на русском языке, содержать не более 3 предложений и сохранять суть оригинала."
        )
    else:
        sys_prompt = "Ты — полезный ассистент. Отвечай четко и по делу."
    return sys_prompt, query.strip()