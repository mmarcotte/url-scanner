from flask import Flask, render_template, request, session
from flask_session import Session

app = Flask(__name__)

urls = [
    {"url": 'https://condepro.com', "health": "200"},
    {"url": 'http://condepro.com/should-nimot-exist', "health": "404"}
]

@app.route("/")
def index():
    # show a table of urls
    # show their health
    return render_template("index.html", urls=urls)

@app.route("/api/url")


