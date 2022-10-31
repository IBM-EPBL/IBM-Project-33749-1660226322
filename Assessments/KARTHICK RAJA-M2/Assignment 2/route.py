import pymongo
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='template')

client = pymongo.MongoClient(
    "mongodb+srv://jjishnu6:CMqL6i2Z1PqHx0yD@cluster0.oca3l9u.mongodb.net/?retryWrites=true&w=majority")
db = client.test.users


@app.route("/")
def hello():
    return render_template('login.html')


@app.route("/home")
def Home():
    return render_template('home.html')


@app.route("/about")
def Blog():
    return render_template('blog.html')


@app.route("/signup", methods=["POST", "GET"])
def Details():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form["password"]

        if (db.find_one({"email": email})):
            return "Users already exits"
        else:
            post = db.insert_one({"email": email, "password": password})
            return render_template('login.html')


@app.route("/login", methods=["POST", "GET"])
def home():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form["password"]

        if (db.find_one({"email": email, "password": password})):
            return render_template('home.html')
        else:
            return "Return Invalid credentials"


@app.route("/register")
def registers():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
