# Сервис аутентификации и авторизации пользователей

Сервис, предоставляющий API для аутентификации и авторизации пользователей, 
позволяющий настроить их роли и права

### Используемые технологии
Язык: python + FastAPI
Сервер: ASGI(uvicorn)
Веб-сервер: Nginx
Хранилище: Postgres
Кеширование: Redis
Контейнеризация: Docker
Тестирование: Pytest

## Установка и запуск
1. Склонировать данный репозиторий c API:
```shell
git clone git@github.com:ReplayForever/Auth_sprint_1.git
```

2. Скопировать настройки переменных окружения из .env.example в .env:
```shell
cp .env.example .env
```

3. Запустить проект через docker-compose для прода ([docker-compose.yml](docker-compose.yml)):
```shell
docker compose up docker-compose.yml
```
Запустить проект через docker-compose для локальной разработки ([docker-compose.dev.yml](docker-compose.dev.yml)):
```shell
docker compose up docker-compose.dev.yml
```

4. Для применения миграций при локальной разработке необходимо находясь в папке [src](src) выполнить команду:
```shell
alembic upgrade head
```

5. Тесты автоматически запускаются после запуска [docker-compose.dev.yml](docker-compose.dev.yml)

Для отдельного запуска тестов необходимо запустить:
```shell
docker compose up docker-compose.dev.yml auth_tests
```
## Переменные окружения

| Variable      | Explanation                                         | Example         |
|---------------|-----------------------------------------------------|-----------------|
| `DB_HOST`     | PostgreSQL Hostname                                 | `auth_postgres` |
| `DB_PASSWORD` | PostgreSQL Password                                 | `password`      |
| `DB_USER`     | PostgreSQL User                                     | `app`           |
| `DB_NAME`     | PostgreSQL Database Name                            | `auth_database` |
| `DB_PORT`     | PostgreSQL Port                                     | `5433`          |
| `REDIS_HOST`  | Redis Hostname                                      | `redis`         |
| `REDIS_PORT`  | Redis Port                                          | `6379`          |
| `AUTH_HOST`   | FastAPI Hostname                                    | `auth`          |
| `AUTH_PORT`   | FastAPI Port                                        | `8002`          |
| `LOG_LEVEL`   | Level of logging                                    | `DEBUG`         |

## OpenAPI
Для проверки работоспособности проекта используется Swagger. 
Запускаем проект и по `http://localhost/api/openapi` переходим на Swagger. Здесь можно проверить работу ендпоинтов

## Console command
Для создания суперюзера необходимо из директории /src в консоли прописать 
```shell
python3 cli.py username login password email
```