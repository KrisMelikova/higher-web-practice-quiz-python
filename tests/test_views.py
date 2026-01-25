import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from quiz.models import Category, Quiz, Question

pytestmark = pytest.mark.django_db

class TestCategoryAPI:
    """Тесты API для категорий"""

    def setup_method(self):
        """Подготовка тестов"""
        self.client = APIClient()
        self.category_data = {'title': 'Science'}

    def test_create_category(self):
        """Тест создания категории через POST /api/category/"""
        url = reverse('category-list')
        response = self.client.post(url, self.category_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Science'
        assert 'id' in response.data
        assert Category.objects.count() == 1
        assert Category.objects.get().title == 'Science'

    def test_create_category_with_empty_title(self):
        """Тест создания категории с пустым названием"""
        url = reverse('category-list')
        response = self.client.post(url, {'title': ''}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_get_categories_list(self):
        """Тест получения списка категорий через GET /api/category/"""
        Category.objects.create(title='Science')
        Category.objects.create(title='History')

        url = reverse('category-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        titles = [cat['title'] for cat in response.data]
        assert 'Science' in titles
        assert 'History' in titles

    def test_get_category_detail(self):
        """Тест получения категории по ID через GET /api/category/<id>/"""
        category = Category.objects.create(title='Science')

        url = reverse('category-detail', args=[category.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Science'
        assert response.data['id'] == category.id

    def test_get_nonexistent_category(self):
        """Тест получения несуществующей категории"""
        url = reverse('category-detail', args=[999])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category(self):
        """Тест обновления категории через PUT /api/category/<id>/"""
        category = Category.objects.create(title='Old Title')

        url = reverse('category-detail', args=[category.id])
        data = {'title': 'New Title'}

        response = self.client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'New Title'

        category.refresh_from_db()
        assert category.title == 'New Title'

    def test_partial_update_category(self):
        """Тест частичного обновления категории через PATCH /api/category/<id>/"""
        category = Category.objects.create(title='Old Title')

        url = reverse('category-detail', args=[category.id])
        data = {'title': 'New Title'}

        response = self.client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'New Title'

    def test_delete_category(self):
        """Тест удаления категории через DELETE /api/category/<id>/"""
        category = Category.objects.create(title='Science')

        url = reverse('category-detail', args=[category.id])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Category.objects.count() == 0

    def test_search_categories_by_title(self):
        """Тест поиска категорий по названию через query параметры"""
        Category.objects.create(title='Science Fiction')
        Category.objects.create(title='Computer Science')
        Category.objects.create(title='History')

        url = reverse('category-list')
        response = self.client.get(url, {'title': 'Science'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        titles = [cat['title'] for cat in response.data]
        assert 'Science Fiction' in titles
        assert 'Computer Science' in titles
        assert 'History' not in titles


class TestQuizAPI:
    """Тесты API для квизов"""

    def setup_method(self):
        """Подготовка тестов"""
        self.client = APIClient()
        self.quiz_data = {
            'title': 'Python Quiz',
            'description': 'Test your Python knowledge'
        }

    def test_create_quiz(self):
        """Тест создания квиза"""
        url = reverse('quiz-list')
        response = self.client.post(url, self.quiz_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Python Quiz'
        assert response.data['description'] == 'Test your Python knowledge'

    def test_get_quizzes_list(self):
        """Тест получения списка квизов"""
        Quiz.objects.create(title='Quiz 1', description='Description 1')
        Quiz.objects.create(title='Quiz 2', description='Description 2')

        url = reverse('quiz-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_quiz_detail(self):
        """Тест получения квиза по ID"""
        quiz = Quiz.objects.create(title='Python Quiz')

        url = reverse('quiz-detail', args=[quiz.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Python Quiz'

    def test_update_quiz(self):
        """Тест обновления квиза"""
        quiz = Quiz.objects.create(title='Old Title')

        url = reverse('quiz-detail', args=[quiz.id])
        data = {'title': 'New Title', 'description': 'New Description'}

        response = self.client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'New Title'

    def test_delete_quiz(self):
        """Тест удаления квиза"""
        quiz = Quiz.objects.create(title='Test Quiz')

        url = reverse('quiz-detail', args=[quiz.id])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Quiz.objects.count() == 0

    def test_search_quizzes_by_title(self):
        """Тест поиска квизов по названию"""
        Quiz.objects.create(title='Python Basics')
        Quiz.objects.create(title='Advanced Python')
        Quiz.objects.create(title='Java Fundamentals')

        url = reverse('quiz-list')
        response = self.client.get(url, {'title': 'Python'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


class TestAPIErrorHandling:
    """Тесты обработки ошибок API"""

    def setup_method(self):
        self.client = APIClient()

    def test_404_for_nonexistent_resources(self):
        """Тест 404 ошибки для несуществующих ресурсов"""
        urls = [
            reverse('category-detail', args=[999]),
            reverse('quiz-detail', args=[999]),
            reverse('question-detail', args=[999]),
        ]

        for url in urls:
            response = self.client.get(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND
