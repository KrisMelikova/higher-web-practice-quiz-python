"""Модуль с контроллерами для категорий"""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from quiz.serializers import CategorySerializer
from quiz.services.category import CategoryService


class CategoryListAPIView(APIView):
    """
    APIView для работы со списком категорий.

    GET /api/category/ — получение всех категорий с фильтрацией
    POST /api/category/ — создание новой категории
    """

    def get(self, request: Request) -> Response:
        """Получение списка категорий"""

        try:
            filters = {}
            title = request.query_params.get('title')
            if title:
                filters['title'] = title

            category_service = CategoryService()
            categories = category_service.list_categories(filters)

            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description='Создание новой категории',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title'],
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Название категории',
                    maxLength=100
                )
            }
        ),
        responses={
            201: openapi.Response('Категория создана', CategorySerializer),
            400: 'Некорректные данные',
            500: 'Внутренняя ошибка сервера'
        }
    )
    def post(self, request: Request) -> Response:
        """Создание новой категории"""

        try:
            title = request.data.get('title', '').strip()

            if not title:
                return Response(
                    {'error': 'Название категории не может быть пустым'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category_service = CategoryService()
            category = category_service.create_category(title)

            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryDetailAPIView(APIView):
    """
    APIView для работы с конкретной категорией.

    GET /api/category/<int:id>/ — получение категории по ID
    PUT /api/category/<int:id>/ — полное обновление категории
    PATCH /api/category/<int:id>/ — частичное обновление категории
    DELETE /api/category/<int:id>/ — удаление категории
    """

    @swagger_auto_schema(
        operation_description='Получение категории по ID',
        responses={
            200: openapi.Response('Категория', CategorySerializer),
            404: 'Категория не найдена',
            400: 'Некорректный запрос'
        }
    )
    def get(self, request: Request, id: int) -> Response:
        """Получение категории по ID"""

        try:
            category_service = CategoryService()
            category = category_service.get_category(id)

            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description='Полное обновление категории',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title'],
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Название категории',
                    maxLength=100
                )
            }
        ),
        responses={
            200: openapi.Response('Категория обновлена', CategorySerializer),
            400: 'Некорректные данные',
            404: 'Категория не найдена'
        }
    )
    def put(self, request: Request, id: int) -> Response:
        """Полное обновление категории"""

        try:
            category_service = CategoryService()
            category = category_service.update_category(id, request.data, partial=False)

            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description='Частичное обновление категории',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Название категории',
                    maxLength=100
                )
            }
        ),
        responses={
            200: openapi.Response('Категория обновлена', CategorySerializer),
            400: 'Некорректные данные',
            404: 'Категория не найдена'
        }
    )
    def patch(self, request: Request, id: int) -> Response:
        """Частичное обновление категории"""

        try:
            category_service = CategoryService()
            category = category_service.update_category(id, request.data, partial=True)

            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description='Удаление категории',
        responses={
            204: 'Категория удалена',
            400: 'Невозможно удалить категорию (есть связанные вопросы)',
            404: 'Категория не найдена'
        }
    )
    def delete(self, request: Request, id: int) -> Response:
        """Удаление категории"""

        try:
            category_service = CategoryService()
            category_service.delete_category(id)

            return Response(
                {'message': 'Категория успешно удалена'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
