"""Модуль с реализацией сервиса квизов"""

from django.db import transaction, DatabaseError
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from quiz.dao import AbstractQuizService
from quiz.models import Quiz


class QuizService(AbstractQuizService):
    """Реализация сервиса для работы с квизами"""

    def list_quizzes(self) -> list[Quiz]:
        """Возвращает список всех квизов."""

        try:
            return list(Quiz.objects.all().order_by('id'))
        except DatabaseError as e:
            raise Exception(f'Ошибка при получении списка квизов: {e}')

    def get_quiz(self, quiz_id: int) -> Quiz:
        """
        Возвращает квиз по его идентификатору.

        :param quiz_id: Идентификатор квиза.
        :return: Квиз из БД.
        """

        try:
            return Quiz.objects.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Exception(f'Квиз c id={quiz_id} не найден')
        except DatabaseError as e:
            raise Exception(f'Ошибка при получении квиза: {e}')

    def get_quizes_by_title(self, title: str) -> list[Quiz]:
        """
        Возвращает список квизов по названию.

        :param title: Название квиза.
        :return: Список квизов с подходящими названиями.
        """

        if not title or len(title.strip()) == 0:
            return []

        try:
            return list(Quiz.objects.filter(
                title__icontains=title.strip()
            ).order_by('title'))
        except DatabaseError as e:
            raise Exception(f'Ошибка при поиске квизов по названию: {e}')

    def create_quiz(self, data: dict) -> Quiz:
        """
        Создает новый квиз.

        :param data: Данные из запроса для создания квиза.
        :return: Созданный квиз.
        """

        title = data.get('title')
        description = data.get('description')

        if not title or len(title.strip()) == 0:
            raise ValidationError('Название квиза не может быть пустым')

        if len(title) > 200:
            raise ValidationError('Название квиза не может превышать 200 символов')

        if description and len(description) > 500:
            raise ValidationError('Описание квиза не может превышать 500 символов')

        try:
            with transaction.atomic():
                return Quiz.objects.create(
                    title=title.strip(),
                    description=description.strip() if description else None
                )
        except DatabaseError as e:
            raise Exception(f'Ошибка при создании квиза: {e}')

    def update_quiz(self, quiz_id: int, data: dict) -> Quiz:
        """
        Обновляет существующий квиз.

        :param quiz_id: Идентификатор квиза.
        :param data: Данные для обновления квиза.
        :return: Обновленный квиз.
        """

        try:
            quiz = self.get_quiz(quiz_id)

            title = data.get('title')
            description = data.get('description')

            if title:
                if not title or len(title.strip()) == 0:
                    raise ValidationError('Название квиза не может быть пустым')
                if len(title) > 200:
                    raise ValidationError('Название квиза не может превышать 200 символов')
                quiz.title = title.strip()

            if description is not None:
                if description and len(description) > 500:
                    raise ValidationError('Описание квиза не может превышать 500 символов')
                quiz.description = description.strip() if description else None

            with transaction.atomic():
                quiz.save()
                return quiz
        except ValidationError as e:
            raise e
        except Exception as e:
            raise Exception(f'Ошибка при обновлении квиза: {e}')

    def delete_quiz(self, quiz_id: int) -> None:
        """
        Удаляет квиз по его идентификатору.

        :param quiz_id: Идентификатор квиза для удаления.
        """

        try:
            quiz = self.get_quiz(quiz_id)

            if quiz.questions.exists():
                raise Exception('Нельзя удалить квиз, к которому привязаны вопросы')

            with transaction.atomic():
                quiz.delete()
        except Exception as e:
            raise Exception(f'Ошибка при удалении квиза: {e}')
