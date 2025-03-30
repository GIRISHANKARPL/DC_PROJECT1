import os
import subprocess
import threading
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import socket
import atexit

app = Flask(__name__, template_folder="templates")
CORS(app)

# Store POS tags received from DC3
pos_tag_results = []
pos_tag_lock = threading.Lock()
processes = []

@app.route('/')
def home():
    """Serve the frontend page (GUI)."""
    return render_template('index.html')

# Function to start a node in a new console window
def run_node(script_name):
    try:
        proc = subprocess.Popen(
            ["python", script_name],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        )
        processes.append(proc)
        print(f"✅ Started: {script_name}")
    except Exception as e:
        print(f"❌ Error starting {script_name}: {e}")

@app.route('/start_nodes', methods=['GET'])
def start_nodes():
    """Starts DC1, DC2, and DC3 nodes."""
    nodes = ["DC1.py", "DC2.py", "DC3.py"]

    for node in nodes:
        threading.Thread(target=run_node, args=(node,)).start()
        time.sleep(5)  # Increase delay for stability

    return jsonify({"message": "✅ Transcription, POS Tagging, and Coordinator nodes started!"})

@app.route('/start_recording', methods=['GET'])
def start_recording():
    """Starts DC0 (audio recording)."""
    threading.Thread(target=run_node, args=("DC0.py",)).start()
    return jsonify({"message": "🎤 Audio recording started!"})

@app.route('/receive_pos_tags', methods=['POST'])
def receive_pos_tags():
    """Receives POS tags from DC3 and stores them."""
    global pos_tag_results
    try:
        data = request.json
        pos_tags = data.get("pos_tags", [])

        if pos_tags:
            with pos_tag_lock:
                pos_tag_results = pos_tags
            return jsonify({"message": "✅ POS tags received successfully!"})
        else:
            return jsonify({"error": "⚠️ No POS tags received"}), 400
    except Exception as e:
        return jsonify({"error": f"⚠️ Error processing POS tags: {e}"}), 500

@app.route('/get_pos_tags', methods=['GET'])
def get_pos_tags():
    """Sends stored POS tags to the frontend."""
    with pos_tag_lock:
        return jsonify({"pos_tags": pos_tag_results})

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0

# Cleanup on exit
def cleanup():
    for proc in processes:
        proc.terminate()
        proc.wait()
    print("🧹 Cleaned up processes!")

atexit.register(cleanup)

if __name__ == '__main__':
    try:
        PORT = 5000
        while is_port_in_use(PORT):
            PORT += 1
        print(f"🚀 Starting Flask backend on port {PORT}...")
        app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
