# URL Scanner
This simple app is to help me monitor the health of a collection of URLs. The goal is to make sure that all of them are returning 200 status codes, and if not do something to make that obvious. 

## Setup
1. clone the repo
1. make sure python and flask is installed
1. make sure a PostgreSQL database is ready
1. install the SQL in install.sql into the database
1. Specify a `DATABASE_URL` environment variable for the database