from flask import Flask, Blueprint, Response, render_template,send_from_directory
from flask_restful import Api, Resource, reqparse
from tauri_updater import tauri_releases_bp

app = Flask(__name__, static_folder='dist', static_url_path='/')
app.register_blueprint(tauri_releases_bp)
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