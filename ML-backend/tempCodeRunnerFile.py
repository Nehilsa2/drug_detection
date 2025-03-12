import pymongo
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import networkx as nx
import plotly.graph_objects as go
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import json
import plotly
from werkzeug.utils import secure_filename
import io
from PIL import Image
from is_Drug import *

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://mayanksahu1005:d3qjjq4ICx30XudJ@cluster0.dceas.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0/")
db = client["test"]
user_collection = db["patterndb"]
interaction_collection = db["interactions"]
flagged_user_collection = db["flaggedusers"]
# Data analysis and plotting function
def analyze_and_plot_data():
    # Fetch user data from MongoDB
    user_data = list(user_collection.find({}, {"_id": 0}))
    df_users = pd.DataFrame(user_data)

    # Check if there's enough data to perform clustering
    if df_users.empty or len(df_users) < 2:
        return None, None

    # Standardize features and perform clustering
    scaler = StandardScaler()
    features = scaler.fit_transform(df_users[['drug_mentions', 'suspicious_words']])
    
    # Choose optimal k (e.g., 3 clusters) for clustering
    k_optimal = 3
    kmeans = KMeans(n_clusters=k_optimal, random_state=42)
    df_users['cluster'] = kmeans.fit_predict(features)

    # K-Means clustering plot between drug mentions and suspicious words
    fig_kmeans = go.Figure()
    for i in range(k_optimal):
        cluster_data = df_users[df_users['cluster'] == i]
        fig_kmeans.add_trace(go.Scatter(
            x=cluster_data['drug_mentions'],
            y=cluster_data['suspicious_words'],
            mode='markers',
            name=f'Cluster {i}',
            marker=dict(size=10)
        ))

    fig_kmeans.update_layout(
        title='K-Means Clustering of Users',
        xaxis_title='Drug Mentions',
        yaxis_title='Suspicious Words'
    )

    # Fetch interaction data to create network graph
    interactions = list(interaction_collection.find({}, {"_id": 0}))
    edges = []

    for conversation in interactions:
        members = conversation['members']
        if len(members) > 1:  # Only consider conversations with multiple members
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    edges.append((members[i], members[j]))

    # Create NetworkX graph and layout
    G = nx.Graph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=42)

    # Prepare data for Plotly graphing
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    node_x, node_y = [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    # Create edge and node traces for Plotly
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    degree_dict = dict(G.degree())
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', hoverinfo='text',
        text=[f"User ID: {node}<br>Connections: {degree_dict[node]}" for node in G.nodes()],
        marker=dict(showscale=True, colorscale='YlGnBu', size=10, colorbar=dict(thickness=15, title='Node Connections'))
    )

    # Create Plotly figure for network graph
    fig_network = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(title='Interactive User Interaction Network', titlefont_size=16,
                                     showlegend=False, hovermode='closest'))

    # Convert figures to JSON for frontend
    kmeans_json = json.dumps(fig_kmeans, cls=plotly.utils.PlotlyJSONEncoder)
    network_json = json.dumps(fig_network, cls=plotly.utils.PlotlyJSONEncoder)
  # Fetch flagged user data
    flagged_users = flagged_user_collection.find({}, {"_id": 0})
    print(flagged_users)
    for user in flagged_users:
        user['suspicious_words'] = user.get('suspicious_words', [])
    # Emit JSON to frontend
    socketio.emit('graph_update', {'kmeans': kmeans_json, 'network': network_json}, namespace='/admin')

# Route to load admin dashboard
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')  # Frontend template

# Trigger analysis and plot update on admin request
@socketio.on('start_analysis', namespace='/admin')
def handle_start_analysis():
    analyze_and_plot_data()



# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def stream_to_image(stream):
    """
    Converts a stream of image data to a PIL Image object.

    Args:
      stream: The stream of image data.

    Returns:
      A PIL Image object.
    """
    image_data = b''  # Initialize an empty bytes object
    for chunk in stream:
        image_data += chunk  # Append each chunk to the bytes object

    # Create an in-memory bytes buffer
    image_buffer = io.BytesIO(image_data)  
    
    # Open the image using Pillow
    image = Image.open(image_buffer)  
    return image

# # Example usage (assuming 'stream' is the fs.createReadStream object)
# image = stream_to_image(stream)

# # Now you can work with the 'image' object (e.g., display, save, process)
# image.show()  # Display the image


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:  # This line should be indented
        return jsonify({'error': 'No image part'}), 400
    if 'text' not in request.form:  # This line should be indented
        return jsonify({'error': 'No text part'}), 400

    image = request.files['image']  # This line should be indented
    text = request.form['text']  # This line should be indented

    if image.filename == '':  # This line should be indented
        return jsonify({'error': 'No selected image'}), 400
    if not allowed_file(image.filename):  # This line should be indented
        return jsonify({'error': 'Invalid image file type'}), 400

    filename = secure_filename(image.filename)  # This line should be indented
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # This line should be indented
    rs = isDrug(filename, text)
    print(rs)
    # Process the image and text here (e.g., save to database, run analysis)
    # ...  # This line should be indented

    return jsonify(rs)  # This line should be indented

@app.route('/', methods=['GET'])
def index():
    sample_text = "have bm1 and ibo last had snow and blow"
    result = detect_drug_keywords(sample_text)
    return result 


# Run app
if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
