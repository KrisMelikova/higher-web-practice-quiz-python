"""Модуль с контроллерами для квизов"""
from typing import Optional

from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from quiz.models import Quiz
from quiz.serializers import QuizSerializer, QuestionSerializer
from quiz.services.question import QuestionService
from quiz.services.quiz_s import QuizService


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с квизами.

    POST /api/quiz — создание квиза.
    GET /api/quiz — получение всех квизов.
    GET /api/quiz/<id:int> — получение квиза по идентификатору.
    PUT /api/quiz/<id:int> — изменение квиза.
    DELETE /api/quiz/<id:int> — удаление квиза.
    """

    serializer_class = QuizSerializer

    def get_queryset(self) -> QuerySet[Quiz]:
        """Возвращает queryset с фильтрацией"""

        queryset = super().get_queryset()

        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def create(self, request:Request, *args, **kwargs) -> Response:
        """Создание квиза через сервис"""

        try:
            quiz_service = QuizService()
            quiz = quiz_service.create_quiz(request.data)

            serializer = self.get_serializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Получение квиза по ID через сервис"""

        try:
            quiz_service = QuizService()
            quiz = quiz_service.get_quiz(int(kwargs['pk']))

            serializer = self.get_serializer(quiz)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Обновление квиза через сервис"""

        try:
            quiz_service = QuizService()
            quiz = quiz_service.update_quiz(
                int(kwargs['pk']),
                request.data
            )

            serializer = self.get_serializer(quiz)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Удаление квиза через сервис"""

        try:
            quiz_service = QuizService()
            quiz_service.delete_quiz(int(kwargs['pk']))

            return Response(
                {'message': 'Квиз успешно удален'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def questions(self, pk: Optional[str] = None) -> Response:
        """Получение вопросов для конкретного квиза"""

        try:
            question_service = QuestionService()
            questions = question_service.get_questions_for_quiz(int(pk))

            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
