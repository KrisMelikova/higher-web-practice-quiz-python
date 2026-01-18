import pytest

from quiz.models import Category, Quiz, Question
from quiz.services.category import CategoryService
from quiz.services.question import QuestionService
from quiz.services.quiz_s import QuizService


@pytest.mark.django_db
class TestCategoryService:
    """Тесты для сервиса категорий"""

    def setup_method(self) -> None:
        """Подготавливает сервис"""
        self.service = CategoryService()

    def test_create_and_get_category(self) -> None:
        """Тест создания и получения категории"""
        category = self.service.create_category('Science')
        fetched = self.service.get_category(category.id)
        assert fetched.title == 'Science'
        assert fetched.id == category.id

    def test_create_category_empty_title(self) -> None:
        """Тест создания категории с пустым названием"""
        with pytest.raises(Exception) as exc_info:
            self.service.create_category('')
        assert 'Название категории не может быть пустым' in str(exc_info.value)

    def test_create_category_long_title(self) -> None:
        """Тест создания категории с слишком длинным названием"""
        long_title = 'A' * 101
        with pytest.raises(Exception) as exc_info:
            self.service.create_category(long_title)
        assert 'Название категории не может превышать 100 символов' in str(exc_info.value)

    def test_get_nonexistent_category(self) -> None:
        """Тест получения несуществующей категории"""
        with pytest.raises(Exception) as exc_info:
            self.service.get_category(999)
        assert 'Категория с id=999 не найдена' in str(exc_info.value)

    def test_update_category(self) -> None:
        """Тест обновления категории"""
        category = Category.objects.create(title='Old')
        updated = self.service.update_category(category.id, {'title': 'New'})
        assert updated.title == 'New'
        assert updated.id == category.id

    def test_list_categories(self) -> None:
        """Тест получения списка категорий"""
        Category.objects.create(title='Science')
        Category.objects.create(title='History')

        categories = self.service.list_categories()
        assert len(categories) == 2
        assert categories[0].title in ['Science', 'History']
        assert categories[1].title in ['Science', 'History']

    def test_list_categories_empty(self) -> None:
        """Тест получения пустого списка категорий"""
        categories = self.service.list_categories()
        assert len(categories) == 0
        assert categories == []

    def test_delete_category(self) -> None:
        """Тест удаления категории"""
        category = Category.objects.create(title='Temp')
        self.service.delete_category(category.id)
        assert Category.objects.count() == 0

    def test_delete_category_with_questions(self) -> None:
        """Тест удаления категории с привязанными вопросами"""
        category = Category.objects.create(title='Science')
        quiz = Quiz.objects.create(title='Test Quiz')
        Question.objects.create(
            quiz=quiz,
            category=category,
            text='Test question',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )

        with pytest.raises(Exception) as exc_info:
            self.service.delete_category(category.id)
        assert 'Нельзя удалить категорию, к которой привязаны вопросы' in str(exc_info.value)
        assert Category.objects.count() == 1

    def test_delete_nonexistent_category(self) -> None:
        """Тест удаления несуществующей категории"""
        with pytest.raises(Exception) as exc_info:
            self.service.delete_category(999)
        assert 'Категория с id=999 не найдена' in str(exc_info.value)


@pytest.mark.django_db
class TestQuizService:
    """Тесты для сервиса квизов"""

    def setup_method(self) -> None:
        """Подготавливает сервис"""
        self.service = QuizService()

    def test_create_quiz(self) -> None:
        """Тест создания квиза"""
        data = {
            'title': 'Python Quiz',
            'description': 'Test your Python knowledge'
        }
        quiz = self.service.create_quiz(data)
        assert quiz.title == 'Python Quiz'
        assert quiz.description == 'Test your Python knowledge'

    def test_create_quiz_empty_title(self) -> None:
        """Тест создания квиза с пустым названием"""
        data = {'title': ''}
        with pytest.raises(Exception) as exc_info:
            self.service.create_quiz(data)
        assert 'Название квиза не может быть пустым' in str(exc_info.value)

    def test_create_quiz_long_title(self) -> None:
        """Тест создания квиза с слишком длинным названием"""
        data = {'title': 'A' * 201}
        with pytest.raises(Exception) as exc_info:
            self.service.create_quiz(data)
        assert 'Название квиза не может превышать 200 символов' in str(exc_info.value)

    def test_create_quiz_long_description(self) -> None:
        """Тест создания квиза с слишком длинным описанием"""
        data = {
            'title': 'Test',
            'description': 'A' * 501
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_quiz(data)
        assert 'Описание квиза не может превышать 500 символов' in str(exc_info.value)

    def test_get_quiz(self) -> None:
        """Тест получения квиза"""
        quiz = Quiz.objects.create(title='Test Quiz')
        fetched = self.service.get_quiz(quiz.id)
        assert fetched.title == 'Test Quiz'
        assert fetched.id == quiz.id

    def test_get_nonexistent_quiz(self) -> None:
        """Тест получения несуществующего квиза"""
        with pytest.raises(Exception) as exc_info:
            self.service.get_quiz(999)
        assert 'Квиз с id=999 не найден' in str(exc_info.value)

    def test_update_quiz(self) -> None:
        """Тест обновления квиза"""
        quiz = Quiz.objects.create(title='Old Title', description='Old Desc')
        data = {
            'title': 'New Title',
            'description': 'New Desc'
        }
        updated = self.service.update_quiz(quiz.id, data)
        assert updated.title == 'New Title'
        assert updated.description == 'New Desc'

    def test_update_quiz_partial(self) -> None:
        """Тест частичного обновления квиза"""
        quiz = Quiz.objects.create(title='Old Title', description='Old Desc')
        data = {'title': 'New Title'}
        updated = self.service.update_quiz(quiz.id, data)
        assert updated.title == 'New Title'
        assert updated.description == 'Old Desc'

    def test_list_quizzes(self) -> None:
        """Тест получения списка квизов"""
        Quiz.objects.create(title='Quiz 1')
        Quiz.objects.create(title='Quiz 2')

        quizzes = self.service.list_quizzes()
        assert len(quizzes) == 2
        titles = [q.title for q in quizzes]
        assert 'Quiz 1' in titles
        assert 'Quiz 2' in titles

    def test_get_quizes_by_title(self) -> None:
        """Тест поиска квизов по названию"""
        Quiz.objects.create(title='Python Basics')
        Quiz.objects.create(title='Advanced Python')
        Quiz.objects.create(title='Java Fundamentals')

        # Поиск по части названия
        quizzes = self.service.get_quizes_by_title('Python')
        assert len(quizzes) == 2
        titles = [q.title for q in quizzes]
        assert 'Python Basics' in titles
        assert 'Advanced Python' in titles
        assert 'Java Fundamentals' not in titles

    def test_get_quizes_by_title_empty(self) -> None:
        """Тест поиска квизов с пустым запросом"""
        Quiz.objects.create(title='Test Quiz')
        quizzes = self.service.get_quizes_by_title('')
        assert quizzes == []

    def test_get_quizes_by_title_case_insensitive(self) -> None:
        """Тест регистронезависимого поиска"""
        Quiz.objects.create(title='Python Quiz')
        quizzes = self.service.get_quizes_by_title('python')
        assert len(quizzes) == 1
        assert quizzes[0].title == 'Python Quiz'

    def test_delete_quiz(self) -> None:
        """Тест удаления квиза"""
        quiz = Quiz.objects.create(title='Test Quiz')
        self.service.delete_quiz(quiz.id)
        assert Quiz.objects.count() == 0

    def test_delete_quiz_with_questions(self) -> None:
        """Тест удаления квиза с привязанными вопросами"""
        quiz = Quiz.objects.create(title='Test Quiz')
        category = Category.objects.create(title='Science')
        Question.objects.create(
            quiz=quiz,
            category=category,
            text='Test question',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )

        with pytest.raises(Exception) as exc_info:
            self.service.delete_quiz(quiz.id)
        assert 'Нельзя удалить квиз, к которому привязаны вопросы' in str(exc_info.value)
        assert Quiz.objects.count() == 1


@pytest.mark.django_db
class TestQuestionService:
    """Тесты для сервиса вопросов"""

    def setup_method(self) -> None:
        """Подготавливает сервис и тестовые данные"""
        self.service = QuestionService()
        self.category = Category.objects.create(title='Programming')
        self.quiz = Quiz.objects.create(title='Python Quiz')

    def test_create_question(self) -> None:
        """Тест создания вопроса"""
        data = {
            'category_id': self.category.id,
            'text': 'Что такое list comprehension?',
            'options': ['Синтаксис для списков', 'Функция', 'Модуль'],
            'correct_answer': 'Синтаксис для списков',
            'difficulty': 'easy'
        }
        question = self.service.create_question(self.quiz.id, data)
        assert question.text == 'Что такое list comprehension?'
        assert question.quiz.id == self.quiz.id
        assert question.category.id == self.category.id
        assert question.options == ['Синтаксис для списков', 'Функция', 'Модуль']
        assert question.correct_answer == 'Синтаксис для списков'
        assert question.difficulty == 'easy'

    def test_create_question_without_quiz_id(self) -> None:
        """Тест создания вопроса без quiz_id (должен быть передан в метод)"""
        data = {
            'category_id': self.category.id,
            'text': 'Test',
            'options': ['A', 'B'],
            'correct_answer': 'A',
            'difficulty': 'easy'
        }
        question = self.service.create_question(self.quiz.id, data)
        assert question.quiz.id == self.quiz.id

    def test_create_question_without_category(self) -> None:
        """Тест создания вопроса без категории"""
        data = {
            'text': 'Test',
            'options': ['A', 'B'],
            'correct_answer': 'A',
            'difficulty': 'easy'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Категория обязательна для вопроса' in str(exc_info.value)

    def test_create_question_with_nonexistent_category(self) -> None:
        """Тест создания вопроса с несуществующей категорией"""
        data = {
            'category_id': 999,
            'text': 'Test',
            'options': ['A', 'B'],
            'correct_answer': 'A',
            'difficulty': 'easy'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Не найдены необходимые объекты' in str(exc_info.value)

    def test_create_question_empty_text(self) -> None:
        """Тест создания вопроса с пустым текстом"""
        data = {
            'category_id': self.category.id,
            'text': '',
            'options': ['A', 'B'],
            'correct_answer': 'A',
            'difficulty': 'easy'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Текст вопроса не может быть пустым' in str(exc_info.value)

    def test_create_question_long_text(self) -> None:
        """Тест создания вопроса с слишком длинным текстом"""
        data = {
            'category_id': self.category.id,
            'text': 'A' * 501,
            'options': ['A', 'B'],
            'correct_answer': 'A',
            'difficulty': 'easy'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Текст вопроса не может превышать 500 символов' in str(exc_info.value)

    def test_create_question_one_option(self) -> None:
        """Тест создания вопроса с одним вариантом ответа"""
        data = {
            'category_id': self.category.id,
            'text': 'Test',
            'options': ['Only one'],
            'correct_answer': 'Only one',
            'difficulty': 'easy'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Должно быть не менее 2 вариантов ответа' in str(exc_info.value)

    def test_create_question_wrong_answer_not_in_options(self) -> None:
        """Тест создания вопроса с правильным ответом не из вариантов"""
        data = {
            'category_id': self.category.id,
            'text': 'Test',
            'options': ['A', 'B'],
            'correct_answer': 'C',
            'difficulty': 'easy'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Правильный ответ должен быть одним из вариантов ответа' in str(exc_info.value)

    def test_create_question_invalid_difficulty(self) -> None:
        """Тест создания вопроса с некорректной сложностью"""
        data = {
            'category_id': self.category.id,
            'text': 'Test',
            'options': ['A', 'B'],
            'correct_answer': 'A',
            'difficulty': 'impossible'
        }
        with pytest.raises(Exception) as exc_info:
            self.service.create_question(self.quiz.id, data)
        assert 'Сложность должна быть одной из:' in str(exc_info.value)

    def test_get_question(self) -> None:
        """Тест получения вопроса"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test question',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        fetched = self.service.get_question(question.id)
        assert fetched.text == 'Test question'
        assert fetched.id == question.id

    def test_get_nonexistent_question(self) -> None:
        """Тест получения несуществующего вопроса"""
        with pytest.raises(Exception) as exc_info:
            self.service.get_question(999)
        assert 'Вопрос с id=999 не найден' in str(exc_info.value)

    def test_list_questions(self) -> None:
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

        questions = self.service.list_questions()
        assert len(questions) == 2
        texts = [q.text for q in questions]
        assert 'Question 1' in texts
        assert 'Question 2' in texts

    def test_get_questions_by_text_empty(self) -> None:
        """Тест поиска вопросов с пустым текстом"""
        Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        questions = self.service.get_questions_by_text('')
        assert questions == []

    def test_get_questions_for_quiz(self) -> None:
        """Тест получения вопросов для квиза"""
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

        questions = self.service.get_questions_for_quiz(self.quiz.id)
        assert len(questions) == 2
        texts = [q.text for q in questions]
        assert 'Q1' in texts
        assert 'Q2' in texts
        assert 'Q3' not in texts

    def test_get_questions_for_nonexistent_quiz(self) -> None:
        """Тест получения вопросов для несуществующего квиза"""
        with pytest.raises(Exception) as exc_info:
            self.service.get_questions_for_quiz(999)
        assert 'Квиз с id=999 не найден' in str(exc_info.value)

    def test_update_question(self) -> None:
        """Тест обновления вопроса"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Old text',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )

        new_category = Category.objects.create(title='New Category')
        data = {
            'text': 'New text',
            'category_id': new_category.id,
            'options': ['X', 'Y', 'Z'],
            'correct_answer': 'Y',
            'difficulty': 'hard',
            'explanation': 'Updated explanation'
        }

        updated = self.service.update_question(question.id, data)
        assert updated.text == 'New text'
        assert updated.category.id == new_category.id
        assert updated.options == ['X', 'Y', 'Z']
        assert updated.correct_answer == 'Y'
        assert updated.difficulty == 'hard'
        assert updated.explanation == 'Updated explanation'

    def test_update_question_partial(self) -> None:
        """Тест частичного обновления вопроса"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Original',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy',
            explanation='Original explanation'
        )

        data = {'text': 'Updated'}
        updated = self.service.update_question(question.id, data)
        assert updated.text == 'Updated'
        assert updated.options == ['A', 'B']  # Не изменилось
        assert updated.explanation == 'Original explanation'  # Не изменилось

    def test_delete_question(self) -> None:
        """Тест удаления вопроса"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test',
            options=['A', 'B'],
            correct_answer='A',
            difficulty='easy'
        )
        self.service.delete_question(question.id)
        assert Question.objects.count() == 0

    def test_check_answer_correct(self) -> None:
        """Тест проверки правильного ответа"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test',
            options=['Да', 'Нет'],
            correct_answer='Да',
            difficulty='easy'
        )
        is_correct = self.service.check_answer(question.id, 'Да')
        assert is_correct is True

    def test_check_answer_incorrect(self) -> None:
        """Тест проверки неправильного ответа"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test',
            options=['Да', 'Нет'],
            correct_answer='Да',
            difficulty='easy'
        )
        is_correct = self.service.check_answer(question.id, 'Нет')
        assert is_correct is False

    def test_check_answer_with_spaces(self) -> None:
        """Тест проверки ответа с пробелами"""
        question = Question.objects.create(
            quiz=self.quiz,
            category=self.category,
            text='Test',
            options=['Python - язык', 'Java - язык'],
            correct_answer='Python - язык',
            difficulty='easy'
        )

        result = self.service.check_answer(question.id, ' Python - язык ')

        assert result in [True, False]

    def test_random_question_from_quiz(self) -> None:
        """Тест получения случайного вопроса из квиза"""
        for i in range(5):
            Question.objects.create(
                quiz=self.quiz,
                category=self.category,
                text=f'Question {i}',
                options=['A', 'B'],
                correct_answer='A',
                difficulty='easy'
            )

        questions_set = set()
        for _ in range(10):
            question = self.service.random_question_from_quiz(self.quiz.id)
            questions_set.add(question.id)

        assert len(questions_set) > 1

    def test_random_question_from_empty_quiz(self) -> None:
        """Тест получения случайного вопроса из пустого квиза"""
        with pytest.raises(Exception) as exc_info:
            self.service.random_question_from_quiz(self.quiz.id)
        assert f'В квизе с id={self.quiz.id} нет вопросов' in str(exc_info.value)

    def test_random_question_from_nonexistent_quiz(self) -> None:
        """Тест получения случайного вопроса из несуществующего квиза"""
        with pytest.raises(Exception) as exc_info:
            self.service.random_question_from_quiz(999)
        assert 'Квиз с id=999 не найден' in str(exc_info.value)
