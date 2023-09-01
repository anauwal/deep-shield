import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask, request, Response, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import argparse
import requests
import time
import threading
from datetime import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
socketio = SocketIO(app)

# Load the trained model
model = tf.keras.models.load_model("sql_injection_detection_model")

# Dictionary to store IP addresses and their activity history
blocked_ips = {}
consecutive_malicious_threshold = 10
block_duration = 600  # 10 minutes
total_prevented_attacks = 0

def is_malicious(query):
    query = str(query).replace('POST / HTTP/1.1', '')
    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts([query])
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_query = pad_sequences(query_sequence, maxlen=100, padding="post")
    prediction = model.predict(np.array(padded_query))
    return prediction > 0.5

@app.route("/", methods=["GET", "POST", "PUT", "DELETE"])
def proxy():
    client_ip = request.remote_addr

    # Check if IP is blocked temporarily
    if client_ip in blocked_ips and time.time() - blocked_ips[client_ip]["timestamp"] < block_duration:
        return Response("IP blocked temporarily due to repeated malicious actions.", status=403)

    query = request.data.decode("utf-8")
  
    if is_malicious(query):
        if client_ip not in blocked_ips:
            blocked_ips[client_ip] = {"count": 1, "timestamp": time.time()}
        else:
            blocked_ips[client_ip]["count"] += 1
            if blocked_ips[client_ip]["count"] >= consecutive_malicious_threshold:
                blocked_ips[client_ip]["timestamp"] = max(blocked_ips[client_ip]["timestamp"], time.time())
                return Response("IP blocked temporarily due to repeated malicious actions.", status=403)
        global total_prevented_attacks
        total_prevented_attacks += 1
        # Return a response for malicious queries
        return Response("Malicious query detected. Access denied.", status=403)
    else:
        if client_ip in blocked_ips:
            blocked_ips[client_ip]["count"] = 0

        target = "http://" + args.target + request.full_path
        response = requests.request(
            method=request.method,
            url=target,
            headers=request.headers,
            data=request.data,
            cookies=request.cookies,
            stream=True
        )
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        headers = [(name, value) for name, value in response.raw.headers.items() if name.lower() not in excluded_headers]
        return Response(response.content, response.status_code, headers)
    
    # Return a default response if none of the conditions are met
    return Response("Request processed successfully.", status=200)

def update_dashboard(socketio):
    while True:
        blocked_ips_data = {ip: {"count": np.random.randint(0, 20), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")} for ip in blocked_ips}
        total_prevented_attacks_data = total_prevented_attacks + np.random.randint(0, 5)

        socketio.emit("update_dashboard", {"blocked_ips": blocked_ips_data, "total_prevented_attacks": total_prevented_attacks_data}, namespace="/dashboard")

        time.sleep(5)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

def main():
    global args
    parser = argparse.ArgumentParser(description="SQL Injection Protection Reverse Proxy")
    parser.add_argument("--target", required=True, help="Target app address (e.g., 127.0.0.1:8000)")
    parser.add_argument("--run", nargs=2, required=True, help="Proxy server address and port (e.g., 0.0.0.0 5000)")
    args = parser.parse_args()

    proxy_host, proxy_port = args.run

    thread = threading.Thread(target=update_dashboard, args=(socketio,))
    thread.start()

    socketio.run(app, host=proxy_host, port=int(proxy_port))

if __name__ == "__main__":
    main()
