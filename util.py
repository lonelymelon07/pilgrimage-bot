import discord
import os
import json

class JsonDB():
    """
    "Temporary" class which will handle JSON files until I can be arsed to learn SQL
    "initialised" here will refer to whether the Bot is currently storing info on that Guild
    """

    @classmethod
    def init_guild(cls, guild: discord.Guild):
        """
        Creates a new file for a guild
        NOTE: This does not check if the guild is already initialised! May wipe all data!
        """ 
        with open(cls.get_guild_file_path(guild), "w") as f:
            f.write(json.dumps({"pilgrimages":{},"members":{}}))


    @classmethod
    def is_guild_init(cls, guild: discord.Guild):
        """Checks to see if the guild has been initialised"""
        return os.path.exists(cls.get_guild_file_path(guild))


    @classmethod
    def add_pilgrimage(cls, guild: discord.Guild, id: str, score: int, display_name: str):
        # NOTE: Does not check to see if guild is initialised!
        
        # Opens the guild file
        with open(cls.get_guild_file_path(guild), "r") as f:
            guild_dict = json.load(f)

        # Writey write
        guild_dict["pilgrimages"][id] = {}
        guild_dict["pilgrimages"][id]["display_name"] = display_name
        guild_dict["pilgrimages"][id]["score"] = score

        # Writes to the file
        with open(cls.get_guild_file_path(guild), "w") as f:
            f.write(json.dumps(guild_dict))


    @classmethod
    def remove_pilgrimage(cls, guild: discord.Guild, id: str) -> int:
        # NOTE: Does not check to see if guild is initialised!

        # Open
        with open(cls.get_guild_file_path(guild), "r") as f:
            guild_dict = json.load(f)

        try:
            guild_dict["pilgrimages"].pop(id)
            success = True
        except KeyError: # dict.pop() raises a KeyError if the specified key does not exist
            success = False

        # Whether we've actually removed something or not, we'll write what we've got
        with open(cls.get_guild_file_path(guild), "w") as f:
            f.write(json.dumps(guild_dict))

        return success


    @classmethod
    def get_pilgrimages(cls, guild: discord.Guild):
        with open(cls.get_guild_file_path(guild), "r") as f:
            return json.load(f)["pilgrimages"]


    @classmethod
    def add_pilgrimage_to_member(cls, guild: discord.Guild, id: str, member: discord.Member):
        # NOTE: Does not check to see if guild is initialised!
        
        # Opens the guild file
        with open(cls.get_guild_file_path(guild), "r") as f:
            guild_dict = json.load(f)

        # If the Member is not already stored we add them
        if str(member.id) not in guild_dict["members"]:
            guild_dict["members"][str(member.id)] = []

        if id not in guild_dict["pilgrimages"]: # Does that ID actually exist?
            success = -2
        elif id not in guild_dict["members"][str(member.id)]: # Has the user already been assigned that pilgrimage?
            guild_dict["members"][str(member.id)].append(id)
            success = 0
        else: # Some other failure (the user already has the pilgrimage)
            success = -1

        # Writes to the file
        with open(cls.get_guild_file_path(guild), "w") as f:
            f.write(json.dumps(guild_dict))

        return success

    @classmethod
    def remove_pilgrimage_from_user(cls, guild: discord.Guild, id:str, member: discord.Member):
        # NOTE: Does not check to see if guild is initialised!
        
        # Opens the guild file
        with open(cls.get_guild_file_path(guild), "r") as f:
            guild_dict = json.load(f)

        if str(member.id) in guild_dict["members"]: # Is the member stored?
            if id in guild_dict["members"][str(member.id)]: # Have they been awarded that pilgrimage?
                guild_dict["members"][str(member.id)].remove(id) # Remove the pilgrimage
                success = 0
            else:
                success = -2 # The user does not have that pilgrimage
        else:
            success = -1 # The user is not yet stored

        # Writes to the file
        with open(cls.get_guild_file_path(guild), "w") as f:
            f.write(json.dumps(guild_dict))

        return success


    @classmethod
    def remove_all_pilgrimages_from_user(cls, guild: discord.Guild, member: discord.Member):
        # NOTE: Does not check to see if guild is initialised!
        
        # Opens the guild file
        with open(cls.get_guild_file_path(guild), "r") as f:
            guild_dict = json.load(f)

        if str(member.id) in guild_dict["members"]:
            guild_dict["members"][str(member.id)].clear()
            success = 0
        else:
            success = -1

        # Writes to the file
        with open(cls.get_guild_file_path(guild), "w") as f:
            f.write(json.dumps(guild_dict))

        return success


    @classmethod
    def get_pilgrimage_display_name(cls, guild: discord.Guild, id: str):
        with open(cls.get_guild_file_path(guild)) as f:
            guild_dict = json.load(f)
        if id in guild_dict["pilgrimages"]:
            return guild_dict["pilgrimages"][id]["display_name"]
        return None


    @staticmethod
    def get_guild_file_path(guild: discord.Guild):
        """Returns the path of the Guild's JSON file (data\1234567890.json)"""
        return os.path.join("data", str(guild.id) + ".json")
