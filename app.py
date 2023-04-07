import os
import openai
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask import request, jsonify
from youtube import get_video_id, get_captions
from models import db, User, Flashcard


app = Flask(__name__)
app.config["SECRET_KEY"] = "5a4379b0d0a662d6d1f14b3f6b1e6d92"
openai.api_key = os.environ.get('OPENAI_API_KEY')  # Replace 'OPENAI_API_KEY' with your actual API key variable name

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database_file.db'  # Replace with your desired database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
@app.before_first_request
def create_tables():
   db.create_all()

def fetch_url_content(url):
   try:
       response = requests.get(url)
       response.raise_for_status()
       soup = BeautifulSoup(response.text, "html.parser")


       paragraphs = soup.find_all("p")
       content = " ".join([p.get_text() for p in paragraphs])
       return content
   except Exception as e:
       print(f"Error fetching content from URL: {e}")
       return ""


@app.route("/", methods=["GET"])
def index():
   return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the user with the same username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("register"))

        # Check if the user with the same email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists. Please use a different email address.")
            return redirect(url_for("register"))

        # Create a new user and add to the database
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password, method="sha256"))
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
   if request.method == "POST":
       email = request.form.get("email")
       password = request.form.get("password")

       user = User.query.filter_by(email=email).first()
       if user and check_password_hash(user.password_hash, password):
           flash("Logged in successfully!")
           return redirect(url_for("index"))
       else:
           flash("Invalid email or password. Please try again")


   return render_template("login.html")


@app.route("/ask", methods=["POST"])
def ask():
   data = request.json
   article = data["article_text"]
   url = data["url"]
   question = data["question"]


   if url:
       fetched_content = fetch_url_content(url)
       if fetched_content:
           article = fetched_content


   prompt = f"{article}\n\nQuestion: {question}\nAnswer:"


   response = openai.Completion.create(
       engine="text-davinci-002",
       prompt=prompt,
       max_tokens=100,
       n=1,
       stop=None,
       temperature=0.5,
   )


   answer = response.choices[0].text.strip()
   return jsonify({"answer": answer})
@app.route("/captions", methods=["POST"])
def captions():
    data = request.get_json()
    video_url = data["video_url"]
    video_id = get_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid video URL"}), 400
    captions = get_captions(video_id)
    if not captions:
        return jsonify({"error": "No captions found for this video"}), 404
    return jsonify(captions)
@app.route('/create_flashcard', methods=['POST'])
def create_flashcard():
    question = request.form.get('question')
    answer = request.form.get('answer')
    user_id = 1  # Replace this with the logged-in user's ID

    flashcard = Flashcard(question=question, answer=answer, user_id=user_id)
    db.session.add(flashcard)
    db.session.commit()

    flash('Flashcard created successfully!')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
   app.run(debug=True)

