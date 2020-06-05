import os
import requests
from requests.exceptions import ConnectionError
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

@app.route("/")
def index():
    urls = get_urls()
    return render_template("index.html", urls=urls)

@app.route("/api/url/<int:id>/scan")
def scan(id):
    # get the URL, and make sure it exists
    row = db.execute('SELECT url FROM urls WHERE id = :id', {"id": id}).fetchone()
    if row is None:
        return jsonify({"error": "Could not locate URL"}), 422

    # make the call, and supply a friendly user agent
    headers = {
        'User-Agent': 'My User Agent 1.0'
    }
    try: 
        res = requests.get(row.url, headers=headers, allow_redirects=False) # allow_redirects=False to catch 30x status_codes
    except ConnectionError:
        return jsonify({"error": "URL call completely failed"}), 422
        

    # save the status update for the history
    db.execute('INSERT INTO health_checks (tstamp, status_code, headers, url_id) VALUES (NOW(), :status_code, :headers, :url_id)', {
        "status_code": res.status_code,
        "headers": json.dumps(dict(res.headers)),
        "url_id": id
    })

    # update our urls table with the latest
    db.execute('UPDATE urls SET status_code = :status_code, headers = :headers, last_update = NOW() WHERE id = :id', {
        "status_code": res.status_code,
        "headers": json.dumps(dict(res.headers)),
        "id": id
    })
    db.commit()

    # respond with some helpful json
    now = datetime.now()
    response = {
        "status_code": res.status_code,
        "last_update": now.strftime("%m/%d/%Y %H:%M:%S")
    }
    if (res.status_code == 302 or res.status_code == 301) and "Location" in dict(res.headers):
        response["redirect_url"] = res.headers["Location"]

    return jsonify(response)

@app.route('/api/url/<int:id>', methods=['DELETE', 'PUT'])
def url_api(id):
    if db.execute('SELECT url FROM urls WHERE id = :id', {"id": id}).rowcount == 0:
        return jsonify({"error": "Invalid url_id"}), 422

    if request.method == 'PUT':
        # Update the URL
        data = request.get_json()
        url = data['url']
        if db.execute('SELECT url FROM urls WHERE url = :url AND id != :id', {"url": url, "id": id}).rowcount != 0:
            delete_url(id)
            return jsonify({"message": "New URL is a dupe of an existing URL; removing old URL", "updated": 0, "removed": 1})

        db.execute('UPDATE urls SET url = :url WHERE id = :id', {"url": url, "id": id})
        db.commit()
        return jsonify({"message": "URL updated", "updated_url": url, "updated": 1})

    if request.method == 'DELETE': 
        # Remove URL from DB
        delete_url(id)
        return jsonify({"message": "URL deleted"})

@app.route('/add', methods=["POST"])
def add():
    # Add the supplied URL
    url = request.form.get("url")
    db.execute("INSERT INTO urls (url) VALUES (:url)", {"url":url})
    db.commit()
    urls = get_urls()
    return render_template("index.html", urls=urls, message="New URL successfully added")

@app.route("/install") # handy route to install DB tables
def install():
    # load install.sql
    f = open('install.sql', 'r')
    sqlFile = f.read()
    f.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        if(command.strip() != ''):
            db.execute(command)
            db.commit()

    # run the commands
    return render_template("install.html", sqlCommands=sqlCommands)

# re-usable query for getting all of the URLS
def get_urls():
    # do not understand why this requires three quotes :(
    return db.execute("""SELECT id, url, headers, status_code, last_update, TO_CHAR(last_update  - INTERVAL '4 hours', 'MM/DD/YYYY HH24:MI:SS') last_update_formatted FROM urls ORDER BY last_update DESC""").fetchall()

def delete_url(id):
    db.execute('DELETE FROM health_checks WHERE url_id = :url_id', {"url_id": id})
    db.execute('DELETE FROM urls WHERE id = :id', {"id": id})
    db.commit()
