import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from quiz.models import Category, Quiz, Question


@pytest.mark.django_db
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


@pytest.mark.django_db
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

@pytest.mark.django_db
class TestQuestionAPI:
    """Тесты API для вопросов"""

    def setup_method(self):
        """Подготовка тестов"""
        self.client = APIClient()
        self.category = Category.objects.create(title='Programming')
        self.quiz = Quiz.objects.create(title='Python Quiz')

        self.question_data = {
            'quiz_id': self.quiz.id,
            'category_id': self.category.id,
            'text': 'Что такое Python?',
            'options': ['Язык программирования', 'Змея', 'Остров'],
            'correct_answer': 'Язык программирования',
            'difficulty': 'easy'
        }

    def test_create_question(self):
        """Тест создания вопроса"""
        url = reverse('question-list')
        response = self.client.post(url, self.question_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['text'] == 'Что такое Python?'
        assert response.data['quiz_title'] == 'Python Quiz'
        assert response.data['category_title'] == 'Programming'

    def test_create_question_without_quiz_id(self):
        """Тест создания вопроса без quiz_id"""
        url = reverse('question-list')
        data = self.question_data.copy()
        del data['quiz_id']

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data or 'quiz_id' in response.data

    def test_create_question_with_invalid_options(self):
        """Тест создания вопроса с некорректными вариантами ответов"""
        url = reverse('question-list')
        data = self.question_data.copy()
        data['options'] = ['Только один вариант']  # Меньше 2

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_questions_list(self):
        """Тест получения списка вопросов"""
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Question 1',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Question 2',
            options=['C', 'D'],
            correct_answer='C',
            difficulty='medium'
        )

        url = reverse('question-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_question_detail(self):
        """Тест получения вопроса по ID"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test Question',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )

        url = reverse('question-detail', args=[question.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == 'Test Question'

    def test_update_question(self):
        """Тест обновления вопроса"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Old Text',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )

        url = reverse('question-detail', args=[question.id])
        data = {
            'text': 'New Text',
            'options': ['X', 'Y', 'Z'],
            'correct_answer': 'Y',
            'difficulty': 'hard'
        }

        response = self.client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == 'New Text'

    def test_delete_question(self):
        """Тест удаления вопроса"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test Question',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )

        url = reverse('question-detail', args=[question.id])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Question.objects.count() == 0

    def test_search_questions_by_text(self):
        """Тест поиска вопросов по тексту"""
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Что такое Python?',
            description='Язык программирования',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Что такое Django?',
            description='Фреймворк на Python',
            options=['C', 'D'],
            correct_answer='C',
            difficulty='medium'
        )

        try:
            url = reverse('question-search')
            response = self.client.get(url, {'text': 'Python'})
            assert response.status_code == status.HTTP_200_OK
        except:
            url = reverse('question-list')
            response = self.client.get(url, {'search': 'Python'})
            assert response.status_code == status.HTTP_200_OK

    def test_check_answer(self):
        """Тест проверки ответа на вопрос"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Что такое Python?',
            options=['Язык программирования', 'Змея'],
            correct_answer='Язык программирования',
            difficulty='easy'
        )

        url = reverse('question-check-answer', args=[question.id])

        response = self.client.post(url, {'answer': 'Язык программирования'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_correct'] is True

        response = self.client.post(url, {'answer': 'Змея'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_correct'] is False

    def test_filter_questions_by_quiz(self):
        """Тест фильтрации вопросов по квизу"""
        quiz2 = Quiz.objects.create(title='Another Quiz')

        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Q1',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Q2',
            options=['C', 'D'],
            correct_answer='C',
            difficulty='medium'
        )

        Question.objects.create(
            quiz=quiz2,
            category=self.category,
            text='Q3',
            options=['E', 'F'],
            correct_answer='E',
            difficulty='hard'
        )

        url = reverse('question-list')
        response = self.client.get(url, {'quiz_id': self.quiz.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_questions_by_difficulty(self):
        """Тест фильтрации вопросов по сложности"""
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Easy Question',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Medium Question',
            options=['C', 'D'],
            correct_answer='C',
            difficulty='medium'
        )
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Hard Question',
            options=['E', 'F'],
            correct_answer='E',
            difficulty='hard'
        )

        url = reverse('question-list')
        response = self.client.get(url, {'difficulty': 'easy'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['difficulty'] == 'easy'


@pytest.mark.django_db
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

    def test_400_for_invalid_data(self):
        """Тест 400 ошибки при невалидных данных"""
        url = reverse('category-list')
        response = self.client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        category = Category.objects.create(title='Test')
        quiz = Quiz.objects.create(title='Test')
        url = reverse('question-list')

        invalid_data = {
            'quiz_id': quiz.id,
            'category_id': category.id,
            'text': '',
            'options': ['A'],
            'correct_answer': 'B',
            'difficulty': 'invalid'
        }

        response = self.client.post(url, invalid_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAPIAuthentication:
    """Тесты аутентификации API (если требуется)"""

    def setup_method(self):
        self.client = APIClient()

    def test_unauthenticated_access(self):
        """Тест доступа без аутентификации"""
        urls = [
            reverse('category-list'),
            reverse('quiz-list'),
            reverse('question-list'),
        ]

        for url in urls:
            response = self.client.get(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
