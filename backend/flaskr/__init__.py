import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify({"success": True, "categories": formatted_categories})
 
    @app.route("/questions", methods=["GET"])
    def get_questions():
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions[start:end],
                "total_questions": len(formatted_questions),
                "categories": formatted_categories,
            }
        )


    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()

        return jsonify({"success": True, "deleted": question_id})

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            question.insert()

            return jsonify({"success": True, "created": question.id})

        except:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        if search_term is None:
            abort(422)

        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
            }
        )
    
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
            }
        )
    
    @app.route("/quizzes", methods=["POST"])
    def get_quiz_question():
        body = request.get_json()
        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        if quiz_category is None:
            abort(422)

        if quiz_category["id"] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == quiz_category["id"]
            ).all()

        formatted_questions = [question.format() for question in questions]

        if len(previous_questions) == len(formatted_questions):
            return jsonify({"success": True})

        random_question = random.choice(formatted_questions)

        while random_question["id"] in previous_questions:
            random_question = random.choice(formatted_questions)

        return jsonify({"success": True, "question": random_question})
    
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not found"}),
            404,
        )
    
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )
    
    return app
