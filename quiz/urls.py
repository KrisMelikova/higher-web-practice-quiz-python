"""Модуль c роутингом"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quiz.views.category import CategoryViewSet
from quiz.views.question import QuestionViewSet
from quiz.views.quiz_v import QuizViewSet

router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'quiz', QuizViewSet, basename='quiz')
router.register(r'question', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
]
