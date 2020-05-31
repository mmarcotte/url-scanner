# URL Scanner
This simple app is to help me monitor the health of a collection of URLs. The goal is to make sure that all of them are returning 200 status codes, and if not do something to make that obvious. 

## Setup
1. make sure python and flask is installed
1. make sure a PostgreSQL database is ready, and specify the following environment variable: 
    ```
    export DATABASE_URL=postgres://example.com
    ```
1. Ensure the application environment variable is set
    ```
    export FLASK_APP=app.py
    ```
1. Install requirements
    ```
    pip3 install -r requirements.txt
    ```
1. Run the application
    ```
    flask run
    ```
1. Browse to the `/install` endpoint to setup the tables and add some sample data