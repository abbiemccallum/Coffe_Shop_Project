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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        #setting up test data
        
        self.new_question = {
        "question": 'What is the capital of Scotland?',
        "answer": 'Edinburgh',
        "category": 3,
        "difficulty": 1
        }

        self.error_question = {
        "question": '',
        "answer": 'Leonardo da Vinci',
        "category": 2,
        "difficulty": 1 
        }
        self.new_quiz = {
        "previous_questions": [],
        "quiz_category": {"type": 'Geography' , "id": 3}
        }

        self.error_quiz = {
        "previous_questions": [],
        "quiz_category": {}
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #test to get categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    #test to get questions
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        
    #test for error when getting questions beyond valid page number
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"difficulty": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #test to delete questions
    def test_delete_question(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)

    #testing error if question does not exist when deleting
    def test_422_question_does_not_exist(self):
        res = self.client().delete("/question/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    #testing creation of new question
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    #testing error when creating new question fails
    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json=self.error_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    #test to search questions by search term
    def test_search_questions(self):
        res = self.client().post("/questions/search", json={"searchTerm": "title"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        
    #test if search is invalid
    def test_search_questions_failure(self):
        res = self.client().post("questions/search", json={"searchTerm": "supercalifragilistic"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #test to get questions by category
    def test_search_questions_by_category(self):
        res = self.client().get("category/1/questions")
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], True)
        self.assertTrue(data["current_category"])

    #test to get question with invalid category
    def test_search_questions_by_category_failure(self):
        res = self.client().get("category/1000/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

   #test to play quiz
    def test_play_quiz(self):
        res = self.client().post("/quizzes", json=self.new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    #testing error in playing quiz
    def test_play_quiz_error(self):
        res = self.client().post("/quizzes", json=self.error_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()