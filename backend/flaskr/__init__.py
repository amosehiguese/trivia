import json
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_quest(req, sel):
    page = req.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [quest.format() for quest in sel]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*":{"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, PATCH, POST, DELETE, PUT, OPTIONS")

        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/categories')
    def retrieve_categories():
        selections = Category.query.order_by(Category.id).all()

        category_list = {sel.id: sel.type for sel in selections}
        return jsonify({
            'success': True,
            'categories': category_list,
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/api/questions')
    def retrieve_questions():
        selections = Question.query.order_by(Question.id).all()

        current_questions = paginate_quest(request, selections)

        categories = Category.query.order_by(Category.id).all()


        category = {cat.id: cat.type for cat in categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selections),
            'current_category': 'All',
            'categories': category
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/api/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id ==  id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/api/questions', methods=['POST'])
    def new_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        try:
            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)

            question.insert()

            return jsonify({
                'success': True
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/api/questions/search', methods=['POST'] )
    def search_term():
        body = request.get_json()
        search = body.get('searchTerm', None)
        
        if search:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()

            # curr_quest = paginate_quest(request, selection)
            curr_quest = [sel.format() for sel in selection]

            return jsonify({
                'success': True,
                'questions': curr_quest,
                'total_questions': len(Question.query.all()),
                'current_category': 'All'
            })

        else:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/api/categories/<int:cat_id>/questions')
    def quest_by_category(cat_id):
        selection = Question.query.filter(Question.category == cat_id).all()

        current_questions = paginate_quest(request, selection)

        cat_type = Category.query.with_entities(Category.type).filter(Category.id == cat_id).all()


        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': cat_type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/api/quizzes', methods=['POST'])
    def play_quiz():

        body = request.get_json()
        previous_questions = body.get('previous_question', None)

        quiz_category = body.get('quiz_category', None)

        questions = Question.query.filter(Question.category == quiz_category['id']).all()

        if previous_questions is None:
            return jsonify({
                'success': True,
                'question': questions[0].format()
            })

        filter_prev_question = [quest.format() for quest in questions if quest.id not in previous_questions]
        
        return jsonify({
                'success': True,
                'question': random.choice(filter_prev_question)
            })




    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False, 
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False, 
            'error': 404,
            'message': 'Not Found',
        }), 404

    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            'success': False, 
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }),422


    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False, 
            'error': 500,
            'message': 'Internal Server Error'
        }), 500
    return app

