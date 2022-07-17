import json
from flask import Response
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS
from flask import flash
import os
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/Dashboard', methods=['GET', 'POST'])
def dashboard():
    basedir = os.path.abspath(os.path.dirname(__file__))
    data_file_display = os.path.join(basedir, 'static/csv-files/MAT517_dataset2.csv')
    # data_file = os.path.join(basedir, 'static/csv-files/MAT517_dataset.csv')

    Linkedin_dataset_display = pd.read_csv(data_file_display)
    # Linkedin_dataset = pd.read_csv(data_file)

    dataset_json_display = Linkedin_dataset_display.to_dict('records')
    # dataset_json = Linkedin_dataset.to_dict('records')

    # members = []
    # for i in range(len(Linkedin_dataset)):
    #     if dataset_json[i]['memberUrn'] not in members:
    #         members.append(dataset_json[i]['memberUrn'])
    #
    # print(len(members))

    # return render_template("dashboard.html")
    return render_template("dashboard.html", dataset = dataset_json_display)

@app.route('/uploads')
def uploads():
    hists = os.listdir('static/uploads')
    hists = [file for file in hists]
    print(hists)
    return render_template('uploads.html', hists=hists)

@app.route('/', methods= ['GET', 'POST'])
def get_message():
    # if request.method == "GET":
    print("Got request in main function")
    return render_template("index.html")

@app.route('/upload_static_file', methods=['POST'])
def upload_static_file():
    print("Got request in static files")
    print(request.files)
    f = request.files['static_file']
    f.save(os.path.join(app.root_path, 'static/uploads/'+f.filename))
    resp = {"success": True, "response": "file saved!"}
    return jsonify(resp), 200