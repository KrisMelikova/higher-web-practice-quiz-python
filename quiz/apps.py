"""Модуль с описанием приложения"""

from django.apps import AppConfig


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'
    verbose_name = 'Сервис для создания вопросов для викторин'
