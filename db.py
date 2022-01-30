"""
A separate file for handling all MySQL Database operations

The database for a guild will be added manually. The name will be formatted as:
guild_<guild.id>

eg.
guild_1234567890

Each database will have three tables:
    Members
        ID
        Score
    Pilgrimages
        ID
        Display Name
        Score
    Members Pilgrimages (linking)
        Member/ID
        Pilgrimage/ID
        Date
"""

import mysql.connector
import json

with open("config.json") as f:
    config = json.load(f)

HOST = config["database"]["host"]
USER = config["database"]["user"]
PASSWORD = config["database"]["password"]

class Database(mysql.connector.MySQLConnection):
    """
    Class for handling all MySQL database operations
    """
    def __init__(self, host:str, user:str, passw:str, guild_id:int):
        super().__init__(
            host=host,
            user=user,
            password=passw,
            database = "guild_" + str(guild_id)
        )

        self.guild_id = guild_id
        self.mycursor = self.cursor()

    def add_pilg(self, id:str, score:int, display_name:str):
        self.mycursor.execute("INSERT INTO pilgrimages (id, display_name, score) VALUES (%s, %s, %s)", (id, display_name, score))
        self.commit()

def guild_db(guild_id:str) -> Database:
    return Database(host=HOST, user=USER, passw=PASSWORD, guild_id=guild_id)