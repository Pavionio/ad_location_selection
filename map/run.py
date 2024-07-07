from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import os.path
from werkzeug.utils import secure_filename
import dill
from joblib import dump, load
from storage import *
from model import *

app = Flask(__name__)
dr = dill.loads(load("dr.joblib"))
ALLOWED_EXTENSIONS = ["json"]


def allowed_file(filename):
    return "." in filename and filename.split(".")[1] in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Основная страница"""
    return render_template("index.html")


@app.route("/api/uploadmarkerfile", methods=["POST"])
def upload_markerfile():
    """Загрузка файла на сервер"""
    file = request.files["file"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if take_information_from_file_storage(file, filename, dr):
            return {"status": "ok"}, 201
    return {"status": "INTERNAL_SERVER_ERROR"}, 500


@app.route("/api/predict", methods=["POST"])
def predict():
    """Предсказание координат топ k точек для выделенных полигонов и для всей карты"""

    number = request.json["number"]
    if request.json.get("coordinates", -1) != -1:
        marks = filter_storage(request.json)
        predicted_coordinates = dr.predict_points(request.json["params"], points=marks, top_k=number, sorted=False)
    else:
        predicted_coordinates = dr.predict_points(request.json["params"], top_k=number, sorted=False)
    return {"predicted_coordinates": predicted_coordinates[["lat", "lon", "weights"]].values.tolist()}, 201


@app.route("/api/heatmappredict", methods=["POST"])
def heat_map_predict():
    """Предсказание координат точек для тепловой карты"""

    predicted_coordinates = dr.predict_points(request.json["params"], sorted=False)
    return {"predicted_coordinates": predicted_coordinates[["lat", "lon", "weights"]].values.tolist()}, 201


@app.route("/api/sendgeo", methods=["POST"])
def send_geo():
    """Отправка на сервер координат полигонов"""
    return geo_storage()


app.run(debug=True)
