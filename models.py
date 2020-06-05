import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Url:

    def __init__(self, id, url):
        self.id = id
        self.url = url

    def update():
        
