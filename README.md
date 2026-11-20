# Асинхронное тестирование FastAPI-приложения

## Что реализовано
Небольшое API для регистрации, входа, просмотра и редактирования профиля. Тесты написаны на `pytest`, `pytest-asyncio` и `httpx.AsyncClient`.

## Запуск в Windows
Откройте терминал в папке проекта:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Тесты используют `httpx.ASGITransport`, поэтому отдельно запускать сервер на localhost не требуется.

## Allure-отчет
```bash
pytest --alluredir=allure-results
allure serve allure-results
```
