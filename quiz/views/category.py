"""Модуль с контроллерами для категорий"""
from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from quiz.models import Category
from quiz.serializers import CategorySerializer
from quiz.services.category import CategoryService


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с категориями.

    POST /api/category — создание категории.
    GET /api/category — получение всех категорий.
    GET /api/category/<id:int> — получение категории по идентификатору.
    PUT /api/category/<id:int> — изменение категории.
    DELETE /api/category/<id:int> — удаление категории.
    """

    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet[Category]:
        """Возвращает queryset с возможностью фильтрации"""

        queryset = super().get_queryset()

        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Создание категории через сервис"""

        try:
            title = request.data.get('title', '').strip()

            if not title:
                return Response(
                    {'error': 'Название категории не может быть пустым'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category_service = CategoryService()
            category = category_service.create_category(title)

            serializer = self.get_serializer(category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Получение категории по ID через сервис"""

        try:
            category_service = CategoryService()
            category = category_service.get_category(int(kwargs['pk']))

            serializer = self.get_serializer(category)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Обновление категории через сервис"""

        try:
            category_service = CategoryService()
            category = category_service.update_category(
                int(kwargs['pk']),
                request.data
            )

            serializer = self.get_serializer(category)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """Частичное обновление категории"""

        return self.update(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Удаление категории через сервис"""

        try:
            category_service = CategoryService()
            category_service.delete_category(int(kwargs['pk']))

            return Response(
                {'message': 'Категория успешно удалена'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
