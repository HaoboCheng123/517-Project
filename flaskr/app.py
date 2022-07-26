from flask import Flask, render_template, request
import networkx as nx
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_file_display = os.path.join(basedir, 'static/csv-files/MAT517_dataset2.csv')
graph_json = os.path.join(basedir, 'static/forcejs/force.json')

Linkedin_dataset_display = pd.read_csv(data_file_display)

dataset_json_display = Linkedin_dataset_display.to_dict('records')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/Dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        form_data = request.form
        data_file = os.path.join(basedir, 'static/csv-files/MAT517_dataset.csv')
        try:
            Linkedin_dataset = pd.read_csv(data_file, nrows=int(form_data['observation_n']))
        except:
            return render_template("dashboard.html", dataset=dataset_json_display, analyze = "undefined", analyze_status = "False")
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
                node_color[mem] = 'steelblue'
                members.append(mem)
            if com not in companies:
                node_value[com] = 0
                node_color[com] = 'red'
                companies.append(com)

        relations_edge = set(relations)

        if form_data['centrality'] == "Follower":
            G = nx.Graph()

            G.add_edges_from(relations_edge)

            nx.set_node_attributes(G, node_color, name="group")

            for edges in G.edges():
                node_value[edges[1]] += node_value[edges[0]]

            nx.set_node_attributes(G, node_value, name="value")

        elif form_data['centrality'] == "Degree":
            G = nx.Graph()

            G.add_edges_from(relations_edge)

            nx.set_node_attributes(G, node_color, name="group")

            centrality = nx.degree_centrality(G)

            for v, c in centrality.items():
                node_value[v] = c

            nx.set_node_attributes(G, node_value, name="value")

        elif form_data['centrality'] == "Betweenness":
            G = nx.Graph()

            G.add_edges_from(relations_edge)

            nx.set_node_attributes(G, node_color, name="group")

            centrality = nx.betweenness_centrality(G)

            for v, c in centrality.items():
                node_value[v] = c

            nx.set_node_attributes(G, node_value, name="value")

        elif form_data['centrality'] == "Closeness":
            G = nx.Graph()

            G.add_edges_from(relations_edge)

            nx.set_node_attributes(G, node_color, name="group")

            centrality = nx.closeness_centrality(G)

            for v, c in centrality.items():
                node_value[v] = c

            nx.set_node_attributes(G, node_value, name="value")

        elif form_data['centrality'] == "PageRank":
            G = nx.DiGraph()

            G.add_edges_from(relations_edge)

            nx.set_node_attributes(G, node_color, name="group")

            centrality = nx.pagerank(G, alpha=0.9)

            for v, c in centrality.items():
                node_value[v] = c

            nx.set_node_attributes(G, node_value, name="value")

        # If use d3 js, then need dump json data to a file
        # json.dump(d, open(graph_json, "w"))
        top_companies = {}
        rank_num = 1

        node_rank = dict(sorted(node_value.items(), key=lambda item: item[1], reverse=True))

        for node in node_rank.keys():
            if node in companies and rank_num <= 10:
                top_companies[rank_num] = node
                rank_num += 1

        # if form_data['centrality'] != "VoteRank":
        #     node_rank = dict(sorted(node_value.items(), key=lambda item: item[1], reverse=True))
        #
        #     for node in node_rank.keys():
        #         if node in companies and rank_num <= 10:
        #             top_companies[rank_num] = node
        #             rank_num += 1
        # else:
        #     for node in centrality:
        #         if rank_num <= 10:
        #             top_companies[rank_num] = node
        #             rank_num += 1

        # Data Normalization
            if node_value:
                minVal = min(node_value.values())
                maxVal = max(node_value.values())
            for key in node_value.keys():
                node_value[key] = (node_value[key] - minVal) / (maxVal - minVal) * 200

        # Average Degree
        average_degree = (sum(x[1] for x in list(G.degree(members))) + sum(x[1] for x in list(G.degree(companies)))) / (len(members) + len(companies))

        #Clustering Coefficient
        clustering_coef = average_degree / (len(members) + len(companies))

        # # Average shortest path (Not feasible, since the graph is weakly connected)
        # average_path = nx.average_shortest_path_length(G)

        # Degree distribution
        from collections import Counter
        degree_counter = [x[1] for x in list(G.degree(members+companies))]
        degree_distribution = Counter(degree_counter)
        degree_distribution_sorted_keys = sorted(degree_distribution.keys())

        plt.hist(degree_counter, bins=(len(members) + len(companies)))
        plt.xlabel("Degree")
        plt.ylabel("Numbers of same degree")
        save_dir = os.path.join(basedir, 'static/uploads/Degree_Distribution.png')
        plt.savefig(save_dir)

        plt.clf()

        if nx.is_directed(G):
            giant_component = G.subgraph(max(nx.strongly_connected_components(G), key=len))
        else:
            giant_component = G.subgraph(max(nx.connected_components(G), key=len))

        pos = nx.spring_layout(giant_component)

        giant_component_node_color = []
        giant_component_node_size = []
        giant_component_label_size = []
        for node in giant_component.nodes():
            giant_component_node_color.append(node_color[node])
            giant_component_node_size.append(node_value[node])
            giant_component_label_size.append(node_value[node]/10)

        if len(giant_component) <=50:
            font_size = 9
        elif len(giant_component)<=100:
            font_size = 6
        else:
            font_size = 4

        nx.draw_networkx_labels(giant_component, font_size=font_size, pos=pos)
        nx.draw(giant_component, pos=pos, node_color=giant_component_node_color, node_size=giant_component_node_size)

        save_dir = os.path.join(basedir, 'static/uploads/Giant_Component.png')
        # save_dir = os.path.join(basedir, 'static/uploads/Giant_Component'+str(version)+'.png')
        plt.savefig(save_dir)

        plt.clf()

        analyze = {
            # "average_path": average_path,
            "clustering_coef": clustering_coef,
            "average_degree": "{:.2f}".format(average_degree),
            "analyze_method": form_data['centrality'],
            "giant_component_size": len(giant_component.nodes()),
            "observation_n": form_data['observation_n'],
            "member_nums": len(members),
            "company_nums": len(companies),
            "edge_nums": len(relations_edge),
        }

        return render_template('dashboard.html', analyze=analyze, dataset=dataset_json, top_companies = top_companies, analyze_status = "True", degree_distribution_sorted_keys = degree_distribution_sorted_keys, degree_distribution = degree_distribution)
    else:
        if os.path.exists(graph_json):
            os.remove(graph_json)
        return render_template("dashboard.html", dataset=dataset_json_display, analyze = "undefined", analyze_status = "False")

# app.run(debug=True)


if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()