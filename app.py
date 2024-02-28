from flask import Flask, request, render_template_string

app = Flask(__name__)


@app.route("/")
def home():
    return render_template_string(open("template.html").read())


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    return f"<h1>Hello, {name}!</h1>"


@app.route("/sample-get", methods=["GET"])
def sample_get():
    return {"message": "This is a GET request response"}


@app.route("/sample-post", methods=["POST"])
def sample_post():
    data = request.json
    return {"message": f"Received data: {data}"}


# TO DO
# 1. check password give time, this include dict check and anything from  https://www.passwordmonster.com/
# 2. do password storing, include salt and challenge.


if __name__ == "__main__":
    app.run(debug=True)
