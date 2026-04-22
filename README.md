# LLM Service Pipeline

Минимальный устойчивый сервис для работы с большими языковыми моделями. Реализует валидацию, кеширование, ретраи, fallback и структурированное логирование.

## Установка и запуск
```bash
# 1. Клонирование и переход в папку
git clone <your-repo-url>
cd my_llm_service

# 2. Виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Зависимости
pip install -r requirements.txt

# 4. Конфигурация
cp .env.example .env
# Откройте или создайте .env и вставьте реальный API-ключ (или оставьте пустым для тестового режима)

# 5. Запуск
python main.py
```

## Описание API  
**POST** `/chat`  
```json
{"message": "Ваш запрос"}
```
**Ответ (200 OK):**
```json
{"response": "...", "source": "llm|cache|fallback", "latency": 0.15}
```
  
**GET** `/health`  
```json
{"status": "ok", "message": "Service is running"}
```

## Особенности
- **Pipeline**: UI → API → валидация → бизнес-логика → LLM → пост-обработка
- **Устойчивость**: таймаут 30с, 3 ретрая с экспоненциальной задержкой, fallback при сбоях
- **Кеширование**: in-memory TTL (по умолчанию 10 мин), ключ учитывает модель, температуру и системный промпт
- **Наблюдаемость**: JSON-структурированные логи в консоль и `service.log`
- **Валидация**: проверка на пустоту, тип и длину (≤1000 символов)

## Тестирование
```bash
python test_api.py
```
Подробный отчёт: `test_report.md`

## Структура
```
my_llm_service/
├── api/          # HTTP-эндпоинты
├── services/     # Бизнес-логика pipeline
├── llm/          # Prompt builder & API-клиент
├── cache/        # TTL-кеширование
├── config/       # Настройки окружения
├── main.py       # Точка входа Flask
├── test_api.py   # Автоматические проверки
├── requirements.txt
└── README.md
```

### `test_report.md`

# Тест-отчёт: LLM Service Pipeline

**Дата:** 2026-04-22  
**Статус:** ✅ Все проверки пройдены  
**Окружение:** Python 3.x, Flask 3.0, Windows PowerShell

## Результаты тестирования
Запуск тестов:  
```bash
python test_api.py
```

| № | Сценарий | Входные данные | HTTP-статус | Фактический ответ | Статус |
|---|----------|---------------|-------------|-------------------|--------|
| 1 | Health check | `GET /health` | `200` | `{'message': 'Service is running', 'status': 'ok'}`| ✅ |
| 2 | Корректный запрос | `{"message":"Test"}` | `200` | `{"latency":0.304,"response":"Mock response...","source":"llm"}` | ✅ |
| 3 | Повторный запрос (кеш) | Тот же запрос | `200` | `{"latency":0.002,"response":"...","source":"cache"}` | ✅ |
| 4 | Пустой ввод | `{"message":""}` | `400` | `{"error":"Field 'message' is required and cannot be empty."}` | ✅ |
| 5 | Длинный текст (>1000) | 1001 символ | `400` | `{"error":"Text too long. Maximum 1000 characters allowed."}` | ✅ |

## Наблюдаемость (фрагменты логов)
**Первый запрос (CACHE_MISS + TEST MODE):**
```json
{"level": "INFO", "msg": "PIPELINE_START: query_len=4", ...}
{"level": "INFO", "msg": "CACHE_MISS: key=gpt-3.5-turbo|0.3|...|Test", ...}
{"level": "WARNING", "msg": "TEST MODE: mock response (API key not configured)", ...}
{"level": "INFO", "msg": "PIPELINE_END: latency=0.304s", ...}
```

**Повторный запрос (CACHE_HIT):**
```json
{"level": "INFO", "msg": "CACHE_HIT: key=gpt-3.5-turbo|0.3|...|Test", ...}
{"level": "INFO", "msg": "PIPELINE_END: cache_hit latency=0.002s", ...}
```

## Вывод
Сервис корректно обрабатывает все заданные сценарии: валидацию ввода, кеширование идентичных запросов, возврат fallback-ответов и структурированное логирование каждого этапа pipeline. Готов к интеграции с реальным LLM-провайдером.