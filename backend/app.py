from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from transformers import pipeline
from dotenv import load_dotenv
import os
from flask_cors import CORS

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
CORS(app)  # Enable CORS for frontend requests

# Initialize the text generation pipeline with GPT-2
generator = pipeline("text-generation", model="gpt2")

@app.route("/api/posts", methods=["GET"])
def get_posts():
    posts = mongo.db.posts.find()
    return jsonify([{"_id": str(p["_id"]), "title": p["title"], "content": p["content"]} for p in posts])

@app.route("/api/posts", methods=["POST"])
def create_post():
    data = request.json
    post_id = mongo.db.posts.insert_one({"title": data["title"], "content": data["content"]}).inserted_id
    return jsonify({"_id": str(post_id), "title": data["title"], "content": data["content"]})

@app.route("/api/suggest", methods=["POST"])
def suggest_content():
    data = request.json
    suggestion = generator(f"Write a blog post about {data['topic']}", max_length=50, num_return_sequences=1)[0]["generated_text"]
    return jsonify({"suggestion": suggestion})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)