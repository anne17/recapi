from flask import Flask, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS

import yaml

app = Flask(__name__, static_url_path='')
CORS(app)
api = Api(app)


DATABASE = "database.yaml"


class Hello(Resource):
    def get(self):
        return {"hello": "true"}

api.add_resource(Hello, '/')


class RecipeList(Resource):
    def get(self):
        return load_data(DATABASE)

api.add_resource(RecipeList, '/recipe-data')


@app.route('/file/<path:path>')
def send_file(path):
    return send_from_directory('res/pdf', path)


def load_data(yamlfile):
    with open(yamlfile) as f:
        return yaml.load(f)

if __name__ == '__main__':
    app.run(debug=True)
