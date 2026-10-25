# Курсовой проект — анализ банковских транзакций

Читает выписку из Excel, считает аналитику, отдаёт JSON для веб-страниц
и сохраняет отчёты в файлы.

## Что сделано

**Страницы (`src/views.py`)**
- `main_page` — приветствие, карты (траты + кешбэк), топ-5, курсы, акции
- `events_page` — расходы/поступления за W/M/Y/ALL, курсы, акции

**Сервисы (`src/services.py`)**
- кешбэк по категориям за месяц
- инвесткопилка (округление до 10/50/100)
- простой поиск, поиск телефонов, переводы физлицам

**Отчёты (`src/reports.py`)**
- траты по категории / по дням недели / рабочий vs выходной
- декоратор `@report` сохраняет результат в `reports/`

## Структура

```
.
├── main.py
├── src/
│   ├── utils.py
│   ├── views.py
│   ├── services.py
│   ├── reports.py
│   ├── external_api.py
│   └── logger.py
├── data/operations.xlsx
├── tests/
├── user_settings.json
└── README.md
```

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pandas openpyxl xlrd requests python-dotenv pytest
```

## Запуск

```bash
python main.py
python main.py --date "2021-12-31 16:44:00" --period M
```

## Настройки

`user_settings.json`:

```json
{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

Курсы — ЦБ РФ (резерв open.er-api.com), акции — Yahoo Finance.
Ошибки API не роняют приложение (кеш / 0.0).

## Тесты

```bash
pytest
```
