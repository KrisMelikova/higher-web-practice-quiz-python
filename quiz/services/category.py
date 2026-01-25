from django.db import transaction, DatabaseError
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404

from quiz.constants import CATEGORY_TITLE_LENGTH
from quiz.dao import AbstractCategoryService
from quiz.models import Category


class CategoryService(AbstractCategoryService):
    """Реализация сервиса для работы с категориями"""

    def list_categories(self, filters: dict = None) -> list[Category]:
        """Метод для получения списка категорий"""

        try:
            queryset = Category.objects.all().order_by('id')

            if filters:
                title = filters.get('title')
                if title:
                    queryset = queryset.filter(title__icontains=title)

            return list(queryset)
        except DatabaseError as e:
            raise Exception(f'Ошибка при получении списка категорий: {e}')
        except Exception as e:
            raise Exception(f'Непредвиденная ошибка: {e}')

    def get_category(self, category_id: int) -> Category:
        """
        Метод для получения категории по идентификатору.

        :param category_id: Идентификатор категории.
        :return: Категория из БД.
        """

        try:
            return get_object_or_404(Category, id=category_id)
        except Http404:
            raise Exception(f'Категория с id={category_id} не найдена')
        except Exception as e:
            raise Exception(f'Ошибка при получении категории: {e}')

    def create_category(self, title: str) -> Category:
        """
        Создает категорию вопросов.

        :param title: Название для категории.
        :return: Созданная категория.
        """

        if not title or len(title.strip()) == 0:
            raise ValidationError('Название категории не может быть пустым')

        if len(title) > CATEGORY_TITLE_LENGTH:
            raise ValidationError(f'Название категории не может превышать '
                                  f'{CATEGORY_TITLE_LENGTH} символов')

        try:
            with transaction.atomic():
                category, created = Category.objects.get_or_create(
                    title=title.strip(),
                    defaults={'title': title.strip()}
                )
                if not created:
                    raise ValidationError(f'Категория с названием "{title}" уже существует')
                return category
        except DatabaseError as e:
            raise Exception(f'Ошибка при создании категории: {e}')
        except Exception as e:
            raise Exception(f'Ошибка при создании категории: {e}')

    def update_category(
            self, category_id: int, data: dict,
            partial: bool = False,
    ) -> Category:
        """
        Обновляет категорию новыми данными.

        :param category_id: Идентификатор категории.
        :param data: Данные для обновления категории.
        :param partial: Частичное обновление (для PATCH).
        :return: Обновленная категория.
        """

        try:
            category = self.get_category(category_id)

            title = data.get('title')
            if title is not None or not partial:
                if title is not None:
                    if not title or len(title.strip()) == 0:
                        raise ValidationError('Название категории не может быть пустым')
                    if len(title) > CATEGORY_TITLE_LENGTH:
                        raise ValidationError(f'Название категории не может превышать '
                                              f'{CATEGORY_TITLE_LENGTH} символов')
                    category.title = title.strip()

            with transaction.atomic():
                category.save()
                return category
        except ValidationError as e:
            raise e
        except Exception as e:
            raise Exception(f'Ошибка при обновлении категории: {e}')

    def delete_category(self, category_id: int) -> None:
        """
        Удаляет категорию.

        :param category_id: Идентификатор категории для удаления.
        """

        try:
            category = self.get_category(category_id)
            if category.questions.exists():
                raise Exception('Нельзя удалить категорию, к которой привязаны вопросы')

            with transaction.atomic():
                category.delete()
        except Exception as e:
            raise Exception(f'Ошибка при удалении категории: {e}')
