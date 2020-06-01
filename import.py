import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f = open('domains.txt', 'r')
contents = f.read()
f.close()

domains = contents.split("\n")

for domain in domains:
    if domain.strip() != '':
        url = 'http://' + domain
        db.execute("INSERT INTO urls (url) VALUES (:url)", {"url":url})

db.commit()
