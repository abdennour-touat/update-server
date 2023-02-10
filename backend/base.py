from flask import Flask, render_template,send_from_directory
from flask_restful import Api, Resource, reqparse

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
api= Api(app)

@app.route('/')
def run():
    return send_from_directory(app.static_folder,"index.html")
@app.route('/api/profile')
def my_profile():
    response_body = {
        "name": "Nagato",
        "about" :"Hello! I'm a full stack developer that loves python and javascript"
    }

    return response_body