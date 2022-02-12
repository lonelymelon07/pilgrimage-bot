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
        self.mycursor = self.cursor(buffered=True)  # IDK why buffered needs to be True but it causes fewer errors lol

    def add_pilg(self, pid:str, score:int, display_name:str):
        self.mycursor.execute("INSERT INTO pilgrimages (id, display_name, score) VALUES (%s, %s, %s);", (pid, display_name, score))
        self.commit()

    def rm_pilg(self, pid:str):
        self.mycursor.execute("DELETE FROM awards WHERE pilgrimage_id = %s;", (pid,))
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

    def list_pilgs(self) -> list[tuple]:
        """
        Return a list of tuples
        Tuples will contain (pid, display_name, score)
        """
        self.mycursor.execute("SELECT * FROM pilgrimages")
        return self.mycursor.fetchall()

    def get_member(self, member:discord.Member|discord.User) -> list[tuple]:
        """
        Return a list tuples of pilgrimages associated with `member`
        In form [(id, display_name, score), ...]
        """

        self.mycursor.execute("SELECT (pilgrimage_id) FROM awards WHERE member_id=%s", (member.id,))
        pids = self.mycursor.fetchall()

        # Have to create a list to store all results, as cursor.fetch*() clears each time a
        # new statement is executed
        results = []

        for i in pids:
            self.mycursor.execute("SELECT * FROM pilgrimages WHERE id=%s", (i[0],))
            results.append(self.mycursor.fetchone())

        return results


    def pilg_exists(self, pid: str) -> bool:
        pilgs = self.list_pilgs()
        for i in pilgs:
            if pid == i[0]:
                return True
        return False


    def member_has_pilg(self, pid:str, member:discord.Member|discord.User) -> bool:
        awards = self.get_member(member)

        if len(awards):
            for i in awards:
                if pid == i[0]:
                    return True
            return False
        return False


def get_db(guild_id:str) -> Database:
    return Database(host=HOST, user=USER, passw=PASSWORD, guild_id=guild_id)

if __name__ == "__main__":
    print("Wrong file dipshit")

    # DEBUG SHIT
    print(get_db(934435062819209296))