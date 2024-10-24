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

    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=YES;TrustServerCertificate=YES'
    conn = pyodbc.connect(connectionString)
    return conn
