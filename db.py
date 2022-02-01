"""
A separate file for handling all MySQL Database operations

The database for a guild will be added manually. The name will be formatted as:
guild_<guild.id>

eg.
guild_1234567890

Each database will have two tables:
    Pilgrimages
        ID (PK)
        Display Name
        Score
    Awards
        Award ID (PK; included only for functionality)
        Pilgrimage/ID (FK)
        Member ID
"""

import mysql.connector
import json
import discord

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

    def add_pilg(self, pid:str, score:int, display_name:str):
        self.mycursor.execute("INSERT INTO pilgrimages (id, display_name, score) VALUES (%s, %s, %s);", (pid, display_name, score))
        self.commit()

    def rm_pilg(self, pid:str):
        self.mycursor.execute("DELETE FROM pilgrimages WHERE id = %s;", (pid,))
        self.commit()

    def award(self, pid:str, member:discord.Member|discord.User):
        self.mycursor.execute("INSERT INTO awards (pilgrimage_id, member_id) VALUES (%s, %s);", (pid, member.id))
        self.commit()

    def revoke(self, pid:str, member:discord.Member|discord.User):
        self.mycursor.execute("DELETE FROM awards WHERE pilgrimage_id = %s AND member_id = %s;", (pid, member.id))
        self.commit()

    def revoke_all(self, member:discord.Member|discord.User):
        self.mycursor.execute("DELETE FROM awards WHERE member_id = %s;", (member.id,))
        self.commit()

def get_db(guild_id:str) -> Database:
    return Database(host=HOST, user=USER, passw=PASSWORD, guild_id=guild_id)

if __name__ == "__main__":
    print("Wrong file dipshit")