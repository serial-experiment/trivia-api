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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        """Test get categories"""
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["categories"])
    
    def test_get_questions(self):
        """Test get questions"""
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_delete_question(self):
        """Test delete question"""
        # write a sqlachemy query to return the highest id from the questions table then use that id to delete the question
        # 
        question = Question.query.order_by(Question.id.desc()).first()  
        question_id = question.id
        res = self.client().delete(f"/questions/{question_id}")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

    def test_delete_question_not_found(self):
        """Test delete question not found"""
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Not found")

    def test_create_question(self):
        """Test create question"""
        res = self.client().post("/questions", json={
            "question": "Test question",
            "answer": "Test answer",
            "category": 1,
            "difficulty": 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

    def test_create_question_bad_request(self):
        """Test create question bad request"""
        res = self.client().post("/questions", json={
            "question": "Test question",
            "answer": "Test answer",
            "category": "Test category"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unprocessable")

    def test_search_questions(self):
        """Test search questions"""
        res = self.client().post("/questions/search", json={
            "searchTerm": "boxer"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_search_questions_bad_request(self):
        """Test search questions bad request"""
        res = self.client().post("/questions/search", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unprocessable")

    def test_get_questions_by_category(self):
        """Test get questions by category"""
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_get_questions_by_category_not_found(self):
        """Test get questions by category not found"""
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 0)

    def test_play_quiz(self):
        """Test play quiz"""
        res = self.client().post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {
                "type": "Test category",
                "id": 1
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])

    def test_play_quiz_bad_request(self):
        """Test play quiz bad request"""
        res = self.client().post("/quizzes", json={
            "previous_questions": []
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()