#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'super-secret-session-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Clear session
class ClearSession(Resource):
    def delete(self):
        session.clear()
        return {}, 204

# List all articles
class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return make_response(jsonify(articles), 200)

# Show article with page view limit logic
class ShowArticle(Resource):
    def get(self, id):
        article = Article.query.filter_by(id=id).first()
        if not article:
            return {'error': 'Article not found'}, 404

        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            return article.to_dict(), 200
        else:
            return {'message': 'Maximum pageview limit reached'}, 401

# Log in
class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {}, 401

# Log out
class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

# Check current session
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
