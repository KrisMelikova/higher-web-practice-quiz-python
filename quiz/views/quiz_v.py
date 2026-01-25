"""Модуль с контроллерами для квизов"""
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from quiz.serializers import QuizSerializer, QuestionSerializer
from quiz.services.question import QuestionService
from quiz.services.quiz_s import QuizService


class QuizListCreateAPIView(APIView):
    """
    APIView для получения списка квизов и создания нового квиза.

    GET /api/quiz/ — получение всех квизов (с возможностью фильтрации по названию)
    POST /api/quiz/ — создание нового квиза
    """

    def get(self, request: Request) -> Response:
        """Получение списка квизов с возможностью фильтрации по названию"""

        try:
            quiz_service = QuizService()
            title = request.query_params.get('title', None)

            if title:
                quizzes = quiz_service.get_quizes_by_title(title)
            else:
                quizzes = quiz_service.list_quizzes()

            serializer = QuizSerializer(quizzes, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description='Создание нового квиза',
        request_body=QuizSerializer,
        responses={
            201: openapi.Response(
                description='Квиз успешно создан',
                schema=QuizSerializer
            ),
            400: openapi.Response(
                description='Ошибка валидации или создания квиза',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            )
        }
    )
    def post(self, request: Request) -> Response:
        """Создание нового квиза"""

        try:
            serializer = QuizSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            quiz_service = QuizService()
            quiz = quiz_service.create_quiz(serializer.validated_data)

            response_serializer = QuizSerializer(quiz)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuizDetailAPIView(APIView):
    """
    APIView для получения, обновления и удаления конкретного квиза.

    GET /api/quiz/<id:int>/ — получение квиза по идентификатору
    PUT /api/quiz/<id:int>/ — полное обновление квиза
    PATCH /api/quiz/<id:int>/ — частичное обновление квиза
    DELETE /api/quiz/<id:int>/ — удаление квиза
    """

    @swagger_auto_schema(
        operation_description='Получение квиза по идентификатору',
        responses={
            200: openapi.Response(
                description='Данные квиза',
                schema=QuizSerializer
            ),
            404: openapi.Response(
                description='Квиз не найден',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            )
        }
    )
    def get(self, request: Request, pk: int) -> Response:
        """Получение квиза по ID"""

        try:
            quiz_service = QuizService()
            quiz = quiz_service.get_quiz(pk)

            serializer = QuizSerializer(quiz)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description='Полное обновление квиза (все поля обязательны)',
        request_body=QuizSerializer,
        responses={
            200: openapi.Response(
                description='Квиз успешно обновлен',
                schema=QuizSerializer
            ),
            400: openapi.Response(
                description='Ошибка валидации или обновления',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Квиз не найден',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            )
        }
    )
    def put(self, request: Request, pk: int) -> Response:
        """Полное обновление квиза"""

        try:
            quiz_service = QuizService()
            quiz = quiz_service.get_quiz(pk)

            serializer = QuizSerializer(quiz, data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            updated_quiz = quiz_service.update_quiz(pk, serializer.validated_data)

            response_serializer = QuizSerializer(updated_quiz)
            return Response(response_serializer.data)

        except Exception as e:
            error_status = status.HTTP_400_BAD_REQUEST
            if 'не найден' in str(e).lower():
                error_status = status.HTTP_404_NOT_FOUND
            return Response(
                {'error': str(e)},
                status=error_status
            )

    @swagger_auto_schema(
        operation_description='Частичное обновление квиза '
                              '(можно обновить только отдельные поля)',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Название квиза',
                    maxLength=200
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Описание квиза',
                    maxLength=500
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='Квиз успешно обновлен',
                schema=QuizSerializer
            ),
            400: openapi.Response(
                description='Ошибка валидации или обновления',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Квиз не найден',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            )
        }
    )
    def patch(self, request: Request, pk: int) -> Response:
        """Частичное обновление квиза"""

        try:
            quiz_service = QuizService()
            quiz = quiz_service.get_quiz(pk)

            serializer = QuizSerializer(quiz, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            updated_quiz = quiz_service.update_quiz(pk, serializer.validated_data)

            response_serializer = QuizSerializer(updated_quiz)
            return Response(response_serializer.data)

        except Exception as e:
            error_status = status.HTTP_400_BAD_REQUEST
            if 'не найден' in str(e).lower():
                error_status = status.HTTP_404_NOT_FOUND
            return Response(
                {'error': str(e)},
                status=error_status
            )

    @swagger_auto_schema(
        operation_description='Удаление квиза',
        responses={
            204: openapi.Response(
                description='Квиз успешно удален'
            ),
            400: openapi.Response(
                description='Ошибка удаления '
                            '(например, у квиза есть привязанные вопросы)',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Квиз не найден',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            )
        }
    )
    def delete(self, request: Request, pk: int) -> Response:
        """Удаление квиза"""

        try:
            quiz_service = QuizService()
            quiz_service.delete_quiz(pk)

            return Response(
                {'message': 'Квиз успешно удален'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            error_status = status.HTTP_400_BAD_REQUEST
            if 'не найден' in str(e).lower():
                error_status = status.HTTP_404_NOT_FOUND
            return Response(
                {'error': str(e)},
                status=error_status
            )


class QuizQuestionsAPIView(APIView):
    """
    APIView для получения вопросов конкретного квиза.

    GET /api/quiz/<quiz_id:int>/questions/ — получение всех вопросов квиза
    """

    @swagger_auto_schema(
        operation_description='Получение всех вопросов для конкретного квиза',
        responses={
            200: openapi.Response(
                description='Список вопросов квиза',
                schema=QuestionSerializer(many=True)
            ),
            404: openapi.Response(
                description='Квиз не найден',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Описание ошибки'
                        )
                    }
                )
            )
        }
    )
    def get(self, request: Request, quiz_id: int) -> Response:
        """Получение вопросов для конкретного квиза"""

        try:
            quiz_service = QuizService()
            quiz_service.get_quiz(quiz_id)

            question_service = QuestionService()
            questions = question_service.get_questions_for_quiz(quiz_id)

            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
