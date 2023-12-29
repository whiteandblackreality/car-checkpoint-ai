# Car-Checkpoint-AI

**Car-Checkpoint-AI** - Это система, позволяющая автоматизировать контроль автомобилей при проезде КПП 

## Содержание
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)

## Архитектура

Архитектура системы выглядит следующим образом: 

<img src="../assets/Car-Checkpoint-AI Architecture v0.1.2.png" alt="Архитектура системы">

## Структура проекта
```
.
├── app                 # Web-приложение системы (back + front)
├── db_repository       # Сервис-репозиторий для общения с PostgreSQL
├── frames_getter       # Микросервис получения кадров из видео потока
└── models_adapter      # Микросервис для общения с Triton Server
```

## Структура БД

<img src="../assets/Car-Checkpoint-AI DB Structure v0.1.4.png" alt="Логическая схема БД">

## Структура S3

<img src="../assets/Car-Checkpoint-AI S3 Structure.png" alt="Структура S3">

## Общий пайплайн обработки

<img src="../assets/Car-Checkpoint-AI Pipeline.png" alt="Пайплайн работы">

## Порты (dev)
- 8679 (db-repository)
- 8683 (WebRTC)