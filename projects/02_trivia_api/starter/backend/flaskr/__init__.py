import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#create pagination
def paginate_questions(request, selection):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # CORS(app)
  CORS(app, resources={r"*": {"origins": "*"}})

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
# CORS Headers
  @app.after_request
  def after_request(response):
      response.headers.add(
          "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
      )
      response.headers.add(
          "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
      )
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #GET Request to retreive categories
  @app.route("/categories")
  def get_categories():
      categories = Category.query.all()
      category_list ={}
      for category in categories:
        category_list[category.id] = category.type
      
      return jsonify(
        {
        "success": True,
        "categories": category_list
        }
      )

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route("/questions")
  def get_questions():
      selection = Question.query.all()
      current_questions = paginate_questions(request, selection)

      #get categories as dictionary
      categories = Category.query.all()
      category_list ={}
      for category in categories:
        category_list[category.id] = category.type
      
      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(selection),
        "categories": category_list,
        "current_category": None})
      
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_questions(question_id):
      #delete question using question id
      try: 
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
          abort(404)

        question.delete()

        return jsonify({
          "success": True
          
        })
      except Exception as e:
       print('Exception is >> ',e )
       abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=["POST"])
  def create_question():
    #retieve input from form
    body = request.get_json()
   
    new_question = body.get("question")
    new_answer = body.get("answer")
    new_difficulty = body.get("difficulty")
    new_category = body.get("category")

    try:

      if None in (new_question, new_answer, new_difficulty, new_category):
       abort(422)
      #insert new data
      else:
        question = Question(question=new_question, answer=new_answer, 
        difficulty=new_difficulty, category=new_category)
        question.insert()

        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          "success":True,
          "created": question.id,
          "questions": current_questions,
          "total_questions": len(selection)
        })
     
    except Exception as e:
      print('Exception is >> ',e )
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions/search", methods=["POST"])
  def search_question():
    body = request.get_json()
    search = body.get("searchTerm")

    try: 
      #search for question using ilike
      selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()

      current_questions = paginate_questions(request, selection)

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(selection),
        "current_category": None
      })
    except Exception as e:
      print('Exception is >> ',e )
      abort(422)
  '''
  '''
  # @TODO: 
  # Create a GET endpoint to get questions based on category. 

  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  # '''
  
  @app.route("/categories/<int:id>/questions")
  def get_questions_category(id):
      try: 
        category = Category.query.get(id)

        if category is None:
          abort(404)
        #get question by category id
        selection = Question.query.filter_by(category=category.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          "success": True,
          "questions": current_questions,
          "total_questions": len(selection),
          "current_category": None
          
        })
      except Exception as e:
       print('Exception is >> ',e )
       abort(422)

  # '''
  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 
  # '''
  @app.route("/quizzes", methods=["POST"])
  def play_quiz():
    body = request.get_json()
    previous_questions = body.get("previous_questions")
    quiz_category = body.get("quiz_category")
    try:
      #if no category, show all
      if quiz_category['id'] == 0: 
         questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
      #show questions with related category
      else:
        questions = Question.query.filter_by(category=quiz_category['id']).filter(
                        Question.id.notin_((previous_questions))).all()
      #return random question   
      if(questions):
        question = random.choice(questions)

      return jsonify({
        "success": True,
        'question':question.format()
      })
  
    except Exception as e:
      print('Exception is >> ',e )
      abort(422)

  # '''
  # @TODO: 
  # Create error handlers for all expected errors 
  # including 404 and 422. 
  # '''
  @app.errorhandler(404)
  def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )

  @app.errorhandler(422)
  def unprocessable(error):
      return (
          jsonify({"success": False, "error": 422, "message": "unprocessable"}),
          422,
      )

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
  return app

    