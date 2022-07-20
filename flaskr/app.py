import json
from flask import Response
from flask import Flask, render_template, request, jsonify
import networkx as nx
import os
import pandas as pd
from networkx.utils import groups

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_file_display = os.path.join(basedir, 'static/csv-files/MAT517_dataset2.csv')
graph_json = os.path.join(basedir, 'static/forcejs/force.json')
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

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/Dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        form_data = request.form
        data_file = os.path.join(basedir, 'static/csv-files/MAT517_dataset.csv')
        Linkedin_dataset = pd.read_csv(data_file, nrows=int(form_data['observation_n']))
        dataset_json = Linkedin_dataset.to_dict('records')
        members = []
        companies = []
        relations = []
        node_color = {}
        node_value = {}

        for i in range(len(Linkedin_dataset)):
            mem = dataset_json[i]['memberUrn'].split(':')[-1]
            mem_follower = dataset_json[i]['followersCount']
            com = dataset_json[i]['companyName']
            relations.append((mem, com))
            if mem not in members:
                node_value[mem] = mem_follower
                node_color[mem] = 1
                members.append(mem)
            if com not in companies:
                node_value[com] = 0
                node_color[com] = 2
                companies.append(com)

        relations_edge = set(relations)
        G = nx.Graph()

        G.add_edges_from(relations_edge)

        nx.set_node_attributes(G, node_color, name="group")

        if form_data['centrality'] == "Follower":
            for edges in G.edges():
                node_value[edges[1]]+=node_value[edges[0]]

            if node_value:
                minVal = min(node_value.values())
                maxVal = max(node_value.values())
            for key in node_value.keys():
                node_value[key] = (node_value[key]-minVal) / (maxVal - minVal)


            nx.set_node_attributes(G, node_value, name="value")

            d = nx.json_graph.node_link_data(G)
        elif form_data['centrality'] == "Degree":
            print(list(nx.degree(members)))


        json.dump(d, open(graph_json, "w"))

        analyze = {
            "observation_n": form_data['observation_n'],
            "member_nums": len(members),
            "company_nums": len(companies),
            "edge_nums": len(relations_edge),
        }
        return render_template('dashboard.html', analyze=analyze, dataset=dataset_json)
    else:
        if os.path.exists(graph_json):
            os.remove(graph_json)
        return render_template("dashboard.html", dataset=dataset_json_display)