from typing import List
from django.contrib import admin

from .models import Category, Quiz, Question


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display: List[str] = ('id', 'title')
    search_fields: List[str] = ('title',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display: List[str] = ('id', 'title', 'description_short')
    search_fields: List[str] = ('title', 'description')

    def description_short(self, obj: Quiz) -> str:
        return obj.description[:50] + '...' if obj.description else ''

    description_short.short_description = 'Описание'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display: List[str] = ('id', 'text_short', 'quiz', 'category', 'difficulty')
    list_filter: List[str] = ('difficulty', 'category', 'quiz')
    search_fields: List[str] = ('text', 'description')

    def text_short(self, obj: Question) -> str:
        return obj.text[:50] + '...'

    text_short.short_description = 'Текст вопроса'
