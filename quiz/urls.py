"""Модуль c роутингом"""

from django.urls import path

from quiz.views.category import CategoryListAPIView, CategoryDetailAPIView
from quiz.views.question import (
    QuestionListCreateView,
    QuestionDetailView, QuestionSearchView,
    QuestionCheckAnswerView, QuestionRandomFromQuizView,
)
from quiz.views.quiz_v import (
    QuizListCreateAPIView, QuizDetailAPIView, QuizQuestionsAPIView,
)

urlpatterns = [
    path('category/', CategoryListAPIView.as_view(), name='category-list'),
    path('category/<int:id>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('quiz/', QuizListCreateAPIView.as_view(), name='quiz-list'),
    path('quiz/<int:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('quiz/<int:quiz_id>/questions/', QuizQuestionsAPIView.as_view(), name='quiz-questions'),
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/search/', QuestionSearchView.as_view(), name='question-search'),
    path('questions/<int:pk>/check-answer/', QuestionCheckAnswerView.as_view(), name='question-check-answer'),
    path('quizzes/<int:quiz_id>/random-question/', QuestionRandomFromQuizView.as_view(),
         name='question-random-from-quiz'),
]
