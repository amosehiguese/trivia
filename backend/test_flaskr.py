import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'test_question',
            'answer': 'test_answer',
            'category': 1,
            'difficulty': 1
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Testing retrieve categories
    def test_retrieve_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])


    # Testing retrieve questions
    def test_retrieve_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])


    # Testing delete question
    def test_delete_question(self):
        question = Question(question='testquest', answer='testans', category=1, difficulty=3)

        question.insert()

        res = self.client().delete('/api/questions/' + str(question.id))

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)


    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/api/questions/1000')
        
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    # searching for questions
    def test_search_term(self):

        res = self.client().post('/api/questions/search', json={'searchTerm': 'autobiography'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'All')

    def test_search_item_not_found(self):
        res = self.client().post('/api/questions/search', json={'searchTerm': 'clincduties'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)


    #Testing new questions
    def test_new_question(self):
        res = self.client().post('/api/questions', json=self.new_question)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_new_question_creation_not_allowed(self):
        res = self.client().post('/api/questions/4', json=self.new_question)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')


    # Testing questions by category

    def test_get_by_categories(self):
        res = self.client().get('/api/categories/1/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_by_categories(self):
        res = self.client().get('/api/categories/1/questions/1')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_quiz(self):
        res = self.client().post('/api/quizzes', json={'quiz_category': {'id': '6', 'type': 'Sport'}, 'previous_category':[12, 1]})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()