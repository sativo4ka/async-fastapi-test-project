# Асинхронное тестирование FastAPI-приложения

## Что реализовано
Небольшое API для регистрации, входа, просмотра и редактирования профиля. Тесты написаны на `pytest`, `pytest-asyncio` и `httpx.AsyncClient`.

## Структура
```text
async_fastapi_test_project/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── pytest.ini
├── requirements.txt
└── report.md
```

## Запуск в Windows
Откройте терминал в папке проекта:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Тесты используют `httpx.ASGITransport`, поэтому отдельно запускать сервер на localhost не требуется.

## Запуск приложения отдельно
```bash
uvicorn app.main:app --reload
```
Документация API будет доступна по адресу `http://127.0.0.1:8000/docs`.

## Allure-отчёт
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## Важное ограничение
Для простоты учебного примера данные хранятся в памяти и очищаются между тестами. При перезапуске приложения пользователи исчезают. Для реального проекта следует использовать БД, полноценное управление токенами и конфигурацию секретов.
