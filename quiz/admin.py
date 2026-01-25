from typing import List
from django.contrib import admin

from .constants import BASE_CHARACTER_LIMIT
from .models import Category, Quiz, Question


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display: List[str] = ('id', 'title')
    search_fields: List[str] = ('title',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display: List[str] = ('id', 'title', 'description_short')
    search_fields: List[str] = ('title', 'description')

    @admin.display(description='Описание')
    def description_short(self, obj: Quiz) -> str:
        return obj.description[:BASE_CHARACTER_LIMIT] if obj.description else ''


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display: List[str] = ('id', 'text_short', 'quiz', 'category', 'difficulty')
    list_filter: List[str] = ('difficulty', 'category', 'quiz')
    search_fields: List[str] = ('text', 'description')

    @admin.display(description='Текст вопроса')
    def text_short(self, obj: Question) -> str:
        return obj.text[:BASE_CHARACTER_LIMIT]
