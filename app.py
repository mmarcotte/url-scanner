import requests
from flask import Flask, render_template, request, session, jsonify
from flask_session import Session

app = Flask(__name__)

urls = [
    {"id": 1, "url": 'https://condepro.com', "health": "200"},
    {"id": 2, "url": 'http://condepro.com/should-nimot-exist', "health": "404"}
]

@app.route("/")
def index():
    # show a table of urls
    # show their health
    return render_template("index.html", urls=urls)

@app.route("/api/scan/<int:id>")
def scan(id):
    # ascertain the URL, and then make a call to check its health
    for row in urls:
        if row["id"] == id:
            url = row["url"]
            print(url)
    res = requests.get(url)
    # save the status update for this URL so we know to show it next time
    # report status update to the requester

    return jsonify({
        "health": res.status_code
        ## maybe include 
    })

# need to add a URL
# need to remove a URL



