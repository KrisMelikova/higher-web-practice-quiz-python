"""Модуль с контроллерами для вопросов"""
from typing import Optional

from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from quiz.models import Question
from quiz.serializers import QuestionSerializer
from quiz.services.question import QuestionService


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с вопросами.

    POST /api/question — создание вопроса.
    GET /api/question — получение всех вопросов.
    GET /api/question/<id:int> — получение вопроса по идентификатору.
    PUT /api/question/<id:int> — изменение вопроса.
    DELETE /api/question/<id:int> — удаление вопроса.
    """

    queryset = Question.objects.all().select_related('quiz', 'category')
    serializer_class = QuestionSerializer

    def get_queryset(self) -> QuerySet[Question]:
        """Возвращает queryset с фильтрацией"""

        queryset = super().get_queryset()

        quiz_id = self.request.query_params.get('quiz_id', None)
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                text__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )

        return queryset.order_by('id')

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Создание вопроса через сервис"""

        try:
            quiz_id = request.data.get('quiz_id')

            if not quiz_id:
                return Response(
                    {'error': 'quiz_id обязателен для создания вопроса'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question_service = QuestionService()
            question = question_service.create_question(
                int(quiz_id),
                request.data
            )

            serializer = self.get_serializer(question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Получение вопроса по ID через сервис"""

        try:
            question_service = QuestionService()
            question = question_service.get_question(int(kwargs['pk']))

            serializer = self.get_serializer(question)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Обновление вопроса через сервис"""

        try:
            question_service = QuestionService()
            question = question_service.update_question(
                int(kwargs['pk']),
                request.data
            )

            serializer = self.get_serializer(question)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Удаление вопроса через сервис"""

        try:
            question_service = QuestionService()
            question_service.delete_question(int(kwargs['pk']))

            return Response(
                {'message': 'Вопрос успешно удален'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'text',
                openapi.IN_QUERY,
                description='Текст для поиска в вопросах',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: QuestionSerializer(many=True),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ))
        }
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_questions(self, request: Request) -> Response:
        """Поиск вопросов по тексту (GET /api/question/search?text=...)"""

        try:
            text = request.query_params.get('text', '').strip()

            if not text:
                return Response(
                    {'error': 'Параметр text обязателен для поиска'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question_service = QuestionService()
            questions = question_service.get_questions_by_text(text)

            serializer = self.get_serializer(questions, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], url_path='random')
    def random_question(self, pk: Optional[str] = None) -> Response:
        """Получение случайного вопроса из квиза (GET /api/question/<quiz_id>/random)"""

        try:
            question_service = QuestionService()
            question = question_service.random_question_from_quiz(int(pk))

            serializer = self.get_serializer(question)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='check-answer')
    def check_answer(self, request: Request, pk: Optional[str] = None) -> Response:
        """Проверка правильности ответа на вопрос (POST /api/question/<id>/check-answer)"""

        try:
            answer = request.data.get('answer', '').strip()

            if not answer:
                return Response(
                    {'error': 'Поле answer обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question_service = QuestionService()
            is_correct = question_service.check_answer(int(pk), answer)

            return Response({
                'is_correct': is_correct,
                'question_id': pk
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
