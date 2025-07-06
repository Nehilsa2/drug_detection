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
from dotenv import load_dotenv, dotenv_values 
from bson import json_util
from collections import Counter
from is_Drug import *
from post_Analysis import post_analysis
from chat_Analysis import chat_analysis

load_dotenv()
# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app,cors_allowed_origins="*")

# Connect to MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["test"]
user_collection = db["patterndb"]
interaction_collection = db["interactions"]
flagged_user_collection = db["flaggedusers"]



# chat_analysis()  # Start monitoring chat messages
# post_analysis()  # Start monitoring posts
def get_flagged_words():
    """
    Fetches flagged words from the database.
    
    Returns:
        list: A list of flagged words.
    """
    flagged_word_data = flagged_user_collection.find({}, {"_id": 0, "suspicious_words": 1})
    flagged_words = []
    for item in flagged_word_data:
        flagged_words.extend(item.get('suspicious_words', []))
        # Count frequency
    frequency = Counter(flagged_words)

    # Separate lists for items and counts
    words_list = list(frequency.keys())
    count_list = list(frequency.values())

    res = {
        "words": words_list,
        "counts": count_list
    }
    return res


# Data analysis and plotting function
def analyze_and_plot_data():


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

    # Use a force-directed layout with more iterations for smoother layout
    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=100)

    # Prepare edge coordinates
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
 
    # Prepare node coordinates
    node_x, node_y = [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    # Compute node degrees for color/size
    degree_dict = dict(G.degree())
    node_color = [degree_dict[node] for node in G.nodes()]
    node_size = [5 + 10 * degree_dict[node] for node in G.nodes()]

    # Edge trace with softer color
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=5, color='rgba(150, 150, 150, 0.4)'),
        hoverinfo='none',
        mode='lines'
    )

    # Node trace with modern colorscale
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[f"<b>User ID:</b> {node}<br><b>Connections:</b> {degree_dict[node]}" for node in G.nodes()],
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            reversescale=True,
            color=node_color,
            size=node_size,
            colorbar=dict(
                thickness=15,
                title='Connections',
                xanchor='left',
                
            ),
            line=dict(width=2, color='DarkSlateGrey')
        )
    )

    # Create Plotly figure
    fig_network = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text='Suspicious Users Connections Network', font=dict(size=20)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=40),
            paper_bgcolor='rgba(231, 76, 60)',
            plot_bgcolor='rgba(231, 76, 60)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )


    # Convert figures to JSON for frontend

    network_json = json.dumps(fig_network, cls=plotly.utils.PlotlyJSONEncoder)


    # Fetch flagged words and their counts
    flagged_words_data = json_util.dumps(get_flagged_words())

  # Fetch flagged user data
    flagged_users = list(flagged_user_collection.find({}, {"_id": 0}))
    json_flagged_users = json_util.dumps(flagged_users, indent=4)
 
    for user in flagged_users:
        user['suspicious_words'] = user.get('suspicious_words', [])
    # Emit JSON to frontend
    socketio.emit('graph_update', {'network': network_json,'flagged_word': flagged_words_data, 'flagged_users': json_flagged_users}, namespace='/admin')

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    socketio.run(app, host="0.0.0.0", port=port)
