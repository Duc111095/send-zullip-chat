import os
from pathlib import Path

import pyodbc
import configparser


def connect_db() -> any:
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.dirname(__file__))+"/config.ini")
    server = config['datasource']['server']
    database = config['datasource']['database']
    username = config['datasource']['username']
    password = config['datasource']['password']

    connectionstring = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(connectionstring)
    return conn
