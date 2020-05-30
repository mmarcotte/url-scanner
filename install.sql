CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    url VARCHAR UNIQUE NOT NULL
);
CREATE TABLE health_checks (
    id SERIAL PRIMARY KEY,
    tstamp TIMESTAMP NOT NULL,
    status_code INTEGER NULL,
    headers JSON NULL,
    url_id INTEGER REFERENCES urls
);


INSERT INTO urls (url) VALUES ('http://www.condepro.com');
INSERT INTO urls (url) VALUES ('http://www.condepro.com/shouldntexi-asdf');