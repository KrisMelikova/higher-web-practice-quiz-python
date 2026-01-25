"""Модуль c моделями приложения quiz"""

from django.db import models
from django.core.exceptions import ValidationError

from quiz.constants import (
    BASE_CHARACTER_LIMIT, CATEGORY_TITLE_LENGTH, CORRECT_ANSWER_LENGTH,
    DIFFICULTY, DESCRIPTION_LENGTH, EXPLANATION_LENGTH, OPTIONS_COUNT,
    TEXT_LENGTH, QUIZ_TITLE_LENGTH,
)


class Category(models.Model):
    """Модель категории вопросов"""

    title = models.CharField(
        max_length=CATEGORY_TITLE_LENGTH,
        verbose_name='Название категории',
        help_text=f'Не более {CATEGORY_TITLE_LENGTH} символов'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']

    def __str__(self):
        return self.title


class Quiz(models.Model):
    """Модель квиза"""

    title = models.CharField(
        max_length=QUIZ_TITLE_LENGTH,
        verbose_name='Название квиза',
        help_text=f'Не более {QUIZ_TITLE_LENGTH} символов'
    )
    description = models.TextField(
        max_length=DESCRIPTION_LENGTH,
        blank=True,
        null=True,
        verbose_name='Описание квиза',
        help_text=f'Не более {DESCRIPTION_LENGTH} символов'
    )

    class Meta:
        verbose_name = 'Квиз'
        verbose_name_plural = 'Квизы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Difficulty(models.TextChoices):
    """Варианты сложностей для вопросов"""

    EASY = 'easy', 'Лёгкий'
    MEDIUM = 'medium', 'Средний'
    HARD = 'hard', 'Сложный'


class Question(models.Model):
    """Модель вопроса"""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Квиз'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Категория'
    )
    text = models.CharField(
        max_length=TEXT_LENGTH,
        verbose_name='Текст вопроса',
        help_text=f'Не более {TEXT_LENGTH} символов'
    )
    description = models.TextField(
        max_length=DESCRIPTION_LENGTH,
        blank=True,
        null=True,
        verbose_name='Описание вопроса',
        help_text=f'Не более {DESCRIPTION_LENGTH} символов'
    )
    options = models.JSONField(
        verbose_name='Варианты ответов',
        help_text=f'Массив с вариантами ответов (минимум {OPTIONS_COUNT} варианта)'
    )
    correct_answer = models.CharField(
        max_length=CORRECT_ANSWER_LENGTH,
        verbose_name='Правильный ответ'
    )
    explanation = models.TextField(
        max_length=EXPLANATION_LENGTH,
        blank=True,
        null=True,
        verbose_name='Объяснение ответа',
        help_text=f'Не более {EXPLANATION_LENGTH} символов'
    )
    difficulty = models.CharField(
        max_length=DIFFICULTY,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        verbose_name='Сложность вопроса'
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['id']

    def __str__(self):
        return f'{self.text[:BASE_CHARACTER_LIMIT]}...'

    def clean(self) -> None:
        """Валидация options перед сохранением"""

        if not isinstance(self.options, list):
            raise ValidationError({'options': 'Options должен быть массивом (списком)'})

        if len(self.options) < OPTIONS_COUNT:
            raise ValidationError({'options': f'Должно быть не менее {OPTIONS_COUNT} вариантов ответа'})

        if self.correct_answer not in self.options:
            raise ValidationError({'correct_answer': 'Правильный ответ '
                                                     'должен быть одним из вариантов '
                                                     'в options'})

    def save(self, *args, **kwargs) -> None:
        """Переопределяем save для вызова clean"""

        self.clean()
        super().save(*args, **kwargs)
