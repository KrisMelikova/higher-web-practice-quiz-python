"""Модуль c сериализаторами"""

from typing import Dict, Any, List, Optional
from rest_framework import serializers

from quiz.models import Category, Quiz, Question


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = ['id', 'title']
        read_only_fields = ['id']

    def validate_title(self, value: str) -> str:
        """Валидация названия категории"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Название категории не может быть пустым')
        if len(value) > 100:
            raise serializers.ValidationError('Название категории не может превышать 100 символов')
        return value


class QuizSerializer(serializers.ModelSerializer):
    """Сериализатор для квизов"""

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description']
        read_only_fields = ['id']

    def validate_title(self, value: str) -> str:
        """Валидация названия квиза"""

        value = value.strip()
        if not value:
            raise serializers.ValidationError('Название квиза не может быть пустым')
        if len(value) > 200:
            raise serializers.ValidationError('Название квиза не может превышать 200 символов')
        return value

    def validate_description(self, value: Optional[str]) -> Optional[str]:
        """Валидация описания квиза"""

        if value and len(value) > 500:
            raise serializers.ValidationError('Описание квиза не может превышать 500 символов')
        return value


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов"""

    quiz_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'quiz_id', 'category_id', 'quiz_title', 'category_title',
            'text', 'description', 'options', 'correct_answer',
            'explanation', 'difficulty'
        ]
        read_only_fields = ['id', 'quiz_title', 'category_title']

    def validate_text(self, value: str) -> str:
        """Валидация текста вопроса"""

        value = value.strip()
        if not value:
            raise serializers.ValidationError('Текст вопроса не может быть пустым')
        if len(value) > 500:
            raise serializers.ValidationError('Текст вопроса не может превышать 500 символов')
        return value

    def validate_description(self, value: Optional[str]) -> Optional[str]:
        """Валидация описания вопроса"""

        if value and len(value) > 500:
            raise serializers.ValidationError('Описание вопроса не может превышать 500 символов')
        return value

    def validate_options(self, value: List[str]) -> List[str]:
        """Валидация вариантов ответа"""

        if not isinstance(value, list):
            raise serializers.ValidationError('Options должен быть массивом')
        if len(value) < 2:
            raise serializers.ValidationError('Должно быть не менее 2 вариантов ответа')
        return value

    def validate_correct_answer(self, value: str) -> str:
        """Валидация правильного ответа"""

        if not value:
            raise serializers.ValidationError('Правильный ответ не может быть пустым')
        return value.strip()

    def validate_explanation(self, value: Optional[str]) -> Optional[str]:
        """Валидация объяснения"""

        if value and len(value) > 250:
            raise serializers.ValidationError('Объяснение не может превышать 250 символов')
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Дополнительная валидация"""

        if 'correct_answer' in data and 'options' in data:
            if data['correct_answer'] not in data['options']:
                raise serializers.ValidationError({
                    'correct_answer': 'Правильный ответ должен быть одним из вариантов ответа'
                })

        quiz_id = data.get('quiz_id')
        category_id = data.get('category_id')

        if quiz_id and not Quiz.objects.filter(id=quiz_id).exists():
            raise serializers.ValidationError({
                'quiz_id': f'Квиз с id={quiz_id} не существует'
            })

        if category_id and not Category.objects.filter(id=category_id).exists():
            raise serializers.ValidationError({
                'category_id': f'Категория с id={category_id} не существует'
            })

        return data

    def create(self, validated_data: Dict[str, Any]) -> Question:
        """Создание вопроса с учетом связей"""

        quiz_id = validated_data.pop('quiz_id')
        category_id = validated_data.pop('category_id')

        quiz = Quiz.objects.get(id=quiz_id)
        category = Category.objects.get(id=category_id)

        return Question.objects.create(
            quiz=quiz,
            category=category,
            **validated_data
        )

    def update(self, instance: Question, validated_data: Dict[str, Any]) -> Question:
        """Обновление вопроса с учетом связей"""

        quiz_id = validated_data.pop('quiz_id', None)
        category_id = validated_data.pop('category_id', None)

        if quiz_id:
            instance.quiz = Quiz.objects.get(id=quiz_id)

        if category_id:
            instance.category = Category.objects.get(id=category_id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
