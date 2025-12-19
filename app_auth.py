import streamlit as st
import sqlite3
import hashlib
import json
import pandas as pd
from datetime import datetime

DB_FILE = "lol_app.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE,
              password TEXT,
              riot_name TEXT,
              riot_tag TEXT)
              ''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS matches
              (id INTEGER PRIMARY KEY AUTOINCREMENT
              user_id INTEGER
              match_id TEXT
              champion TEXT
              jso_data TEXT
              upload_data TIMESTAMP
              FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()

# Sécurise le mot de passe
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, make_hash(password)))
    data = c.fetchall()
    conn.close()
    return data[0] if data else None