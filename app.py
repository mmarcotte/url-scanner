#
# @todo
# - give api routes perhaps some parameters (like what fields for the status report)
# 
# 
# 

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

# get the urls with the specified status_code
@app.route("/api/url/status/<int:status_code>")
def get_urls_with_status(status_code):
    rows = db.execute("""SELECT id, url, headers, status_code, last_update, TO_CHAR(last_update  - INTERVAL '4 hours', 'MM/DD/YYYY HH24:MI:SS') last_update_formatted FROM urls WHERE status_code = :status_code ORDER BY last_update ASC""", {
        "status_code": status_code
    }).fetchall()
    urls = []
    for row in rows:
        urls.append(row["url"])
    return jsonify(urls)

@app.route("/api/url/status")
def get_status_codes():
    rows = db.execute("SELECT status_code, COUNT(*) AS count FROM urls GROUP BY status_code ORDER BY count DESC").fetchall()
    results = []
    for row in rows:
        results.append({"status_code": row["status_code"], "count": row["count"]})
    return jsonify(results)

@app.route("/api/url/<int:id>/scan")
def scan(id):
    # get the URL, and make sure it exists
    now = datetime.now()
    row = db.execute('SELECT url FROM urls WHERE id = :id', {"id": id}).fetchone()
    if row is None:
        return jsonify({"error": "Could not locate URL"}), 422

    # make the call, and supply a friendly user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Cache-Control': 'no-cache',
        'Referer': 'https://www.google.com'
    }
    try: 
        res = requests.get(row.url, headers=headers, allow_redirects=False) # allow_redirects=False to catch 30x status_codes
    except ConnectionError as errc:
        print("Error connecting: ", errc)
        db.execute('UPDATE urls SET status_code = :status_code, last_update = NOW() WHERE id = :id', {
            "status_code": 0,
            "id": id
        })
        db.commit()
        return jsonify({
            "error": str(errc), 
            "url": row.url,
            "last_update": now.strftime("%m/%d/%Y %H:%M:%S")
        }), 422


    # update our urls table with the latest
    db.execute('UPDATE urls SET status_code = :status_code, headers = :headers, last_update = NOW() WHERE id = :id', {
        "status_code": res.status_code,
        "headers": json.dumps(dict(res.headers)),
        "id": id
    })
    db.commit()

    # respond with some helpful json
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

@app.route('/api/cleanup', methods=["DELETE"])
def cleanup():
    sql = 'TRUNCATE health_checks'
    db.execute(sql)
    db.commit()
    return jsonify({"message":"Health Checks database has been purged"})


# re-usable query for getting all of the URLS
def get_urls():
    # do not understand why this requires three quotes :(
    return db.execute("""SELECT id, url, headers, status_code, last_update, TO_CHAR(last_update  - INTERVAL '4 hours', 'MM/DD/YYYY HH24:MI:SS') last_update_formatted FROM urls ORDER BY last_update ASC""").fetchall()

def delete_url(id):
    db.execute('DELETE FROM health_checks WHERE url_id = :url_id', {"url_id": id})
    db.execute('DELETE FROM urls WHERE id = :id', {"id": id})
    db.commit()
