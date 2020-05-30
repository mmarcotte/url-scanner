import requests
from flask import Flask, render_template, request, session, jsonify
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

@app.route("/api/scan")
def scan():
    url = request.args.get('url')
    res = requests.get(url)
    return jsonify({
        "health": res.status_code
    })



    # fetch the URL
    # return JSON about health
# need to add a URL
# need to remove a URL



