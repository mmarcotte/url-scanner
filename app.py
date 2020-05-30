import os
import requests
import json
from flask import Flask, render_template, request, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

urls = db.execute('SELECT * FROM urls ORDER BY last_update DESC').fetchall()

@app.route("/")
def index():
    # show a table of urls
    # show their health
    return render_template("index.html", urls=urls)

@app.route("/api/scan/<int:id>")
def scan(id):
    # ascertain the URL, and then make a call to check its health
    row = db.execute('SELECT url FROM urls WHERE id = :id', {"id": id}).fetchone()
    res = requests.get(row.url)

    # save the status update for this URL so we know to show it next time
    db.execute('INSERT INTO health_checks (tstamp, status_code, headers, url_id) VALUES (NOW(), :status_code, :headers, :url_id)', {
        "status_code": res.status_code,
        "headers": json.dumps(dict(res.headers)),
        "url_id": id
    })

    db.execute('UPDATE urls SET status_code = :status_code, headers = :headers, last_update = NOW() WHERE id = :id', {
        "status_code": res.status_code,
        "headers": json.dumps(dict(res.headers)),
        "id": id
    })
    db.commit()

    return jsonify({
        "status_code": res.status_code
    })

# need to add a URL
# need to remove a URL

@app.route("/install")
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


