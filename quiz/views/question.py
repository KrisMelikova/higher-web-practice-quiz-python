"""View для работы с вопросами"""
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from quiz.serializers import QuestionSerializer
from quiz.services.question import QuestionService


class QuestionListCreateView(APIView):
    """View для получения списка вопросов и создания нового"""

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('quiz_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('difficulty', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={
            200: QuestionSerializer(many=True),
            400: 'Bad Request'
        }
    )
    def get(self, request: Request) -> Response:
        """Получение списка вопросов"""
        try:
            filters = {
                'quiz_id': request.query_params.get('quiz_id'),
                'category_id': request.query_params.get('category_id'),
                'difficulty': request.query_params.get('difficulty'),
                'search': request.query_params.get('search'),
            }

            questions = QuestionService.list_questions(filters)
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        request_body=QuestionSerializer,
        responses={
            201: QuestionSerializer,
            400: 'Bad Request'
        }
    )
    def post(self, request: Request) -> Response:
        """Создание нового вопроса"""
        try:
            serializer = QuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            question = QuestionService.create_question(serializer.validated_data)

            response_serializer = QuestionSerializer(question)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuestionDetailView(APIView):
    """View для работы с конкретным вопросом"""

    @swagger_auto_schema(
        responses={
            200: QuestionSerializer,
            404: 'Not Found'
        }
    )
    def get(self, request: Request, pk: int) -> Response:
        """Получение вопроса по ID"""
        try:
            question = QuestionService.get_question(pk)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        request_body=QuestionSerializer,
        responses={
            200: QuestionSerializer,
            400: 'Bad Request'
        }
    )
    def put(self, request: Request, pk: int) -> Response:
        """Полное обновление вопроса"""
        try:
            serializer = QuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            question = QuestionService.update_question(pk, serializer.validated_data)

            response_serializer = QuestionSerializer(question)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        request_body=QuestionSerializer,
        responses={
            200: QuestionSerializer,
            400: 'Bad Request'
        }
    )
    def patch(self, request:Request, pk:int) -> Response:
        """Частичное обновление вопроса"""
        try:
            question = QuestionService.get_question(pk)
            serializer = QuestionSerializer(question, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            updated_question = QuestionService.update_question(pk, serializer.validated_data)

            response_serializer = QuestionSerializer(updated_question)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, pk: int) -> Response:
        """Удаление вопроса"""
        try:
            QuestionService.delete_question(pk)
            return Response(
                {'message': 'Вопрос успешно удален'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuestionSearchView(APIView):
    """View для поиска вопросов"""

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('text', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            200: QuestionSerializer(many=True),
            400: 'Bad Request'
        }
    )
    def get(self, request: Request) -> Response:
        """Поиск вопросов по тексту"""
        try:
            text = request.query_params.get('text', '').strip()

            if not text:
                return Response(
                    {'error': 'Параметр text обязателен для поиска'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            questions = QuestionService.search_by_text(text)
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuestionCheckAnswerView(APIView):
    """View для проверки ответа на вопрос"""

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['answer'],
            properties={
                'answer': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'question_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: 'Bad Request'
        }
    )
    def post(self, request: Request, pk: int) -> Response:
        """Проверка ответа на вопрос"""
        try:
            answer = request.data.get('answer', '').strip()

            if not answer:
                return Response(
                    {'error': 'Поле answer обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_correct = QuestionService.check_answer(pk, answer)

            return Response({
                'is_correct': is_correct,
                'question_id': pk
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuestionRandomFromQuizView(APIView):
    """View для получения случайного вопроса из квиза"""

    @swagger_auto_schema(
        responses={
            200: QuestionSerializer,
            404: 'Not Found'
        }
    )
    def get(self, request: Request, quiz_id: int) -> Response:
        """Получение случайного вопроса из квиза"""

        try:
            question_service = QuestionService()
            question = question_service.random_question_from_quiz(quiz_id)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
