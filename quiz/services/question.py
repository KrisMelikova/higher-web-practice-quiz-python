"""Модуль с реализацией сервиса вопросов"""
import random

from django.db import transaction, DatabaseError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q

from quiz.constants import DESCRIPTION_LENGTH, EXPLANATION_LENGTH, OPTIONS_COUNT, TEXT_LENGTH
from quiz.dao import AbstractQuestionService
from quiz.models import Category, Difficulty, Quiz, Question


class QuestionService(AbstractQuestionService):
    """Реализация сервиса для работы с вопросами"""

    def list_questions(self) -> list[Question]:
        """
        Возвращает список всех вопросов.

        :return: Список вопросов.
        """

        try:
            return list(Question.objects.all()
                        .select_related('quiz', 'category')
                        .order_by('id'))
        except DatabaseError as e:
            raise Exception(f'Ошибка при получении списка вопросов: {e}')

    def get_question(self, question_id: int) -> Question:
        """
        Возвращает вопрос по его идентификатору.

        :param question_id: Идентификатор вопроса.
        :return: Вопрос из БД.
        """

        try:
            return Question.objects.select_related('quiz', 'category').get(id=question_id)
        except ObjectDoesNotExist:
            raise Exception(f'Вопрос с id={question_id} не найден')
        except DatabaseError as e:
            raise Exception(f'Ошибка при получении вопроса: {e}')

    def get_questions_by_text(self, text: str) -> list[Question]:
        """
        Возвращает вопрос по его тексту.

        :param text: Текст вопроса.
        :return: Вопрос из БД.
        """

        if not text or len(text.strip()) == 0:
            return []

        try:
            return list(Question.objects.filter(
                Q(text__icontains=text.strip()) |
                Q(description__icontains=text.strip())
            ).select_related('quiz', 'category').order_by('id'))
        except DatabaseError as e:
            raise Exception(f'Ошибка при поиске вопросов по тексту: {e}')

    def get_questions_for_quiz(self, quiz_id: int) -> list[Question]:
        """
        Получение вопросов по идентификатору квиза.

        :param quiz_id: Идентификатор квиза.
        :return: Список вопросов квиза.
        """

        try:
            Quiz.objects.get(id=quiz_id)

            return list(Question.objects.filter(quiz_id=quiz_id)
                        .select_related('category')
                        .order_by('id'))
        except ObjectDoesNotExist:
            raise Exception(f'Квиз c id={quiz_id} не найден')
        except DatabaseError as e:
            raise Exception(f'Ошибка при получении вопросов квиза: {e}')

    def create_question(self, quiz_id: int, data: dict) -> Question:
        """
        Создает новый вопрос.

        :param quiz_id: Идентификатор квиза, к которому относится вопрос.
        :param data: Данные из запроса для создания вопроса.
        :return: Созданный вопрос.
        """

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            category_id = data.get('category_id')
            category = Category.objects.get(id=category_id) if category_id else None

            if not category:
                raise ValidationError('Категория обязательна для вопроса')

            text = data.get('text')
            options = data.get('options')
            correct_answer = data.get('correct_answer')
            difficulty = data.get('difficulty')

            if not text or len(text.strip()) == 0:
                raise ValidationError('Текст вопроса не может быть пустым')
            if len(text) > DESCRIPTION_LENGTH:
                raise ValidationError(f'Текст вопроса не может '
                                      f'превышать {DESCRIPTION_LENGTH} символов')

            description = data.get('description')
            if description and len(description) > DESCRIPTION_LENGTH:
                raise ValidationError(f'Описание вопроса не может '
                                      f'превышать {DESCRIPTION_LENGTH} символов')

            if not correct_answer:
                raise ValidationError('Правильный ответ обязателен')

            if correct_answer not in options:
                raise ValidationError('Правильный ответ должен быть одним из '
                                      'вариантов ответа')

            if difficulty not in [d[0] for d in Difficulty.choices]:
                raise ValidationError(f'Сложность должна быть одной '
                                      f'из: {[d[0] for d in Difficulty.choices]}')

            explanation = data.get('explanation')
            if explanation and len(explanation) > EXPLANATION_LENGTH:
                raise ValidationError(f'Объяснение ответа не может превышать '
                                      f'{EXPLANATION_LENGTH} символов')

            with transaction.atomic():
                return Question.objects.create(
                    quiz=quiz,
                    category=category,
                    text=text.strip(),
                    description=description.strip() if description else None,
                    options=options,
                    correct_answer=correct_answer,
                    explanation=explanation.strip() if explanation else None,
                    difficulty=difficulty
                )
        except ObjectDoesNotExist as e:
            raise Exception(f'Не найдены необходимые объекты: {e}')
        except ValidationError as e:
            raise e
        except DatabaseError as e:
            raise Exception(f'Ошибка при создании вопроса: {e}')

    def update_question(self, question_id: int, data: dict) -> Question:
        """
        Обновляет существующий вопрос.

        :param question_id: Идентификатор вопроса.
        :param data: Данные для обновления вопроса.
        :return: Обновленный вопрос.
        """

        try:
            question = self.get_question(question_id)

            category_id = data.get('category_id')
            if category_id:
                category = Category.objects.get(id=category_id)
                question.category = category

            text = data.get('text')
            if text:
                if not text or len(text.strip()) == 0:
                    raise ValidationError('Текст вопроса не может быть пустым')
                if len(text) > TEXT_LENGTH:
                    raise ValidationError(f'Текст вопроса не может '
                                          f'превышать {TEXT_LENGTH} символов')
                question.text = text.strip()

            description = data.get('description')
            if description is not None:
                if description and len(description) > DESCRIPTION_LENGTH:
                    raise ValidationError(f'Описание вопроса не может превышать '
                                          f'{DESCRIPTION_LENGTH} символов')
                question.description = description.strip() if description else None

            options = data.get('options')
            if options:
                if not isinstance(options, list) or len(options) < OPTIONS_COUNT:
                    raise ValidationError(f'Должно быть не менее {OPTIONS_COUNT} вариантов '
                                          f'ответа в виде списка')
                question.options = options

            correct_answer = data.get('correct_answer')
            if correct_answer:
                current_options = options if options else question.options
                if correct_answer not in current_options:
                    raise ValidationError('Правильный ответ должен быть одним из вариантов ответа')
                question.correct_answer = correct_answer

            difficulty = data.get('difficulty')
            if difficulty:
                if difficulty not in [d[0] for d in Difficulty.choices]:
                    raise ValidationError(
                        f'Сложность должна быть одной из: {[d[0] for d in Difficulty.choices]}')
                question.difficulty = difficulty

            explanation = data.get('explanation')
            if explanation is not None:
                if explanation and len(explanation) > EXPLANATION_LENGTH:
                    raise ValidationError(f'Объяснение ответа не может '
                                          f'превышать {EXPLANATION_LENGTH} символов')
                question.explanation = explanation.strip() if explanation else None

            with transaction.atomic():
                question.save()
                return question
        except ObjectDoesNotExist as e:
            raise Exception(f'Категория не найдена: {e}')
        except ValidationError as e:
            raise e
        except Exception as e:
            raise Exception(f'Ошибка при обновлении вопроса: {e}')

    def delete_question(self, question_id: int) -> None:
        """
        Удаляет вопрос по его идентификатору.

        :param question_id: Идентификатор вопроса для удаления.
        """

        try:
            question = self.get_question(question_id)

            with transaction.atomic():
                question.delete()
        except Exception as e:
            raise Exception(f'Ошибка при удалении вопроса: {e}')

    def check_answer(self, question_id: int, answer: str) -> bool:
        """
        Проверяет ответ на вопрос.

        :param question_id: Идентификатор вопроса.
        :param answer: Ответ пользователя.
        :return: True, если ответ правильный, False - в противном случае.
        """

        try:
            question = self.get_question(question_id)
            return question.correct_answer.strip().lower() == answer.strip().lower()
        except Exception as e:
            raise Exception(f'Ошибка при проверке ответа: {e}')

    def random_question_from_quiz(self, quiz_id: int) -> Question:
        """
        Возвращает случайный вопрос из указанного квиза.

        :param quiz_id: Идентификатор квиза.
        :return: Случайный вопрос из квиза.
        """

        try:
            Quiz.objects.get(id=quiz_id)

            questions = Question.objects.filter(quiz_id=quiz_id)

            if not questions.exists():
                raise Exception(f'B квизе c id={quiz_id} нет вопросов')

            count = questions.count()
            random_index = random.randint(0, count - 1)
            return questions.all()[random_index]

        except ObjectDoesNotExist:
            raise Exception(f'Квиз c id={quiz_id} не найден')
        except Exception as e:
            raise Exception(f'Ошибка при получении случайного вопроса: {e}')
