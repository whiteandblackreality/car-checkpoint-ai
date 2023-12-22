# Car-Checkpoint-AI MVP v0.4.0

**Car-Checkpoint-AI** - Это система, позволяющая автоматизировать контроль автомобилей при проезде КПП 

Первоначальная идея описана <a href="ex_readmes/README.md">здесь</a>

## Содержание
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)

## Архитектура

Архитектура системы выглядит следующим образом: 

<img src="assets/Car-Checkpoint-AI Architecture v0.4.0.png" alt="Архитектура системы">

## Структура проекта
```
.
├── app                 # Web-приложение системы (back)
├── db_repository       # Сервис-репозиторий для общения с PostgreSQL
├── frames_getter       # Микросервис получения кадров из видео потока
└── models              # Адаптеры к моделям
```

## Структура БД

<img src="assets/Car-Checkpoint-AI DB Structure v0.4.0.png" alt="Логическая схема БД">

## Общий пайплайн обработки

<img src="assets/Car-Checkpoint-AI Pipeline v0.4.0.png" alt="Пайплайн работы">
