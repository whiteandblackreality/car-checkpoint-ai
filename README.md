# Car-Checkpoint-AI v0.1.0

**Car-Checkpoint-AI** - Это система, позволяющая автоматизировать контроль автомобилей при проезде КПП 

## Содержание
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)

## Архитектура

Архитектура системы выглядит следующим образом: 

<img src="assets/Car-Checkpoint-AI Architecture.png" alt="Архитектура системы">

## Структура проекта
```
.
├── app                 # Web-приложение системы (back + front)
├── db_repository       # Сервис-репозиторий для общения с PostgreSQL
├── video_getter        # Микросервис получения видео потока
├── frames_processing   # Микросервис обработки видеопотока, извлечение кадров
└── models_adapter      # Микросервис для общения с Triton Server
```

## Структура БД

<img src="assets/Car-Checkpoint-AI DB Structure.png" alt="Логическая схема БД">

## Структура S3

<img src="assets/Car-Checkpoint-AI S3 Structure.png" alt="Структура S3">

## Общий пайплайн обработки

<img src="assets/Car-Checkpoint-AI Pipeline.png" alt="Пайплайн работы">
