import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from sklearn.utils import compute_class_weight

# Load the CSV dataset
data = pd.read_csv("clean_sql_dataset.csv")

# Separate queries and labels
queries = data["Query"].tolist()
labels = data["Label"].tolist()

# Tokenization and padding
tokenizer = Tokenizer(num_words=5000)  # Limit vocabulary size for better generalization
tokenizer.fit_on_texts(queries)
sequences = tokenizer.texts_to_sequences(queries)
padded_sequences = pad_sequences(sequences, maxlen=100, padding="post")  # Limit sequence length

# Convert labels to numpy arrays
y_labels = np.array(labels)

# Split data into training, validation, and testing sets
X_train, X_temp, y_train, y_temp = train_test_split(padded_sequences, y_labels, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Calculate class weights for handling class imbalance
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train).tolist()

# Build a more complex model architecture
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=128, input_length=100),
    tf.keras.layers.Conv1D(128, 5, activation='relu'),
    tf.keras.layers.GlobalMaxPooling1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss="binary_crossentropy", optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              metrics=["accuracy"])

# Train the model with class weights and validation
model.fit(X_train, y_train, epochs=15, batch_size=64, validation_data=(X_val, y_val),
          class_weight=dict(enumerate(class_weights)))


# Evaluate the model on the test set
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test loss: {loss:.4f}, Test accuracy: {accuracy:.4f}")

# Save the trained model in SavedModel format
model.save("sql_injection_detection_model")
