"""Модуль c моделями приложения quiz"""

from django.db import models


class Category(models.Model):
    """Модель категории вопросов"""

    title = models.CharField(
        max_length=100,
        verbose_name='Название категории',
        help_text='Не более 100 символов'
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
        max_length=200,
        verbose_name='Название квиза',
        help_text='Не более 200 символов'
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание квиза',
        help_text='Не более 500 символов'
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
        max_length=500,
        verbose_name='Текст вопроса',
        help_text='Не более 500 символов'
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание вопроса',
        help_text='Не более 500 символов'
    )
    options = models.JSONField(
        verbose_name='Варианты ответов',
        help_text='Массив с вариантами ответов (минимум 2 варианта)'
    )
    correct_answer = models.CharField(
        max_length=500,
        verbose_name='Правильный ответ'
    )
    explanation = models.TextField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name='Объяснение ответа',
        help_text='Не более 250 символов'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        verbose_name='Сложность вопроса'
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['id']

    def __str__(self):
        return f'{self.text[:50]}...'

    def clean(self) -> None:
        """Валидация options перед сохранением"""

        from django.core.exceptions import ValidationError

        if not isinstance(self.options, list):
            raise ValidationError({'options': 'Options должен быть массивом (списком)'})

        if len(self.options) < 2:
            raise ValidationError({'options': 'Должно быть не менее 2 вариантов ответа'})

        if self.correct_answer not in self.options:
            raise ValidationError({'correct_answer': 'Правильный ответ должен быть одним из вариантов в options'})

    def save(self, *args, **kwargs) -> None:
        """Переопределяем save для вызова clean"""

        self.clean()
        super().save(*args, **kwargs)
