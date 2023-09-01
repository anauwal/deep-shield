from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST", "PUT", "DELETE"])
def handle_request():
    data = {
        "method": request.method,
        "headers": dict(request.headers),
        "data": request.data.decode("utf-8"),
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
