import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask, request, jsonify

# Load the trained model
model = tf.keras.models.load_model("sql_injection_detection_model")

# Load the tokenizer
tokenizer = Tokenizer()
tokenizer_path = "tokenizer.pkl"  # Path to your saved tokenizer
tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_path)

app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query = data["query"]

    # Preprocess the query for the model
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_query = pad_sequences(query_sequence, padding="post")

    # Make a prediction using the model
    prediction = model.predict(np.array(padded_query))

    # Decide whether to allow or block the query
    if prediction > 0.5:
        result = {"message": "Malicious query detected. Access denied."}
        return jsonify(result), 403
    else:
        # Process the query and return the appropriate response
        # Replace this with your application logic
        result = {"message": "Query processed successfully."}
        return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
