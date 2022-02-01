import discord
from discord.ext import commands
from util import JsonDB
import db
from db import get_db

with open("token.txt") as f:
    TOKEN = f.read()

client = commands.Bot(command_prefix = ";")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.command()
async def init(ctx):
    """Initialises the Guild's storage of pilgrimages"""
    async with ctx.typing():
        if JsonDB.is_guild_init(ctx.guild):
            await ctx.send("Guild has already been initialised!")
        else:
            JsonDB.init_guild(ctx.guild)
            await ctx.send("Guild initialised!")

    print(f"{ctx.author} has run command init in #{ctx.channel}")


@client.command(name="add")
async def add_pilgrimage(ctx, pid:str, score:int, *, display_name:str=""):
    """Adds a pilgrimage"""
    if not pid.isidentifier(): # Ensures that `id` is a valid identifier
        await ctx.send("ID must contain only alphanumeric characters and underscores, and cannot start with a number!")
        return

    # If there was no display name, we will set it to the id
    if not display_name:
        display_name = pid

    get_db(ctx.guild.id).add_pilg(pid, score, display_name)

    await ctx.send(f"Pilgrimage **{display_name}** created!\nScore: {score}\nID: `{pid}`")

    print(f"{ctx.author} has run command add in #{ctx.channel}")


@client.command(name="remove", aliases=["rm", "delete", "del"])
async def remove_pilgrimage(ctx, pid:str):
    """Removes an existing pilgrimage"""

    get_db(ctx.guild.id).rm_pilg(pid)
    
    await ctx.send("Deleted the pilgrimage")
        

@client.command(name="list")
async def list_pilgrimages(ctx):
    """Lists all pilgrimages"""
    async with ctx.typing():
        pilgrimages = JsonDB.get_pilgrimages(ctx.guild)
        
        output = ""
        if len(pilgrimages) >= 1:
            # k will be the id, v will be a dict of other data
            for k, v in pilgrimages.items():
                output += f"\n**{v['display_name']}:**"
                output += f"\n\tScore: {v['score']}"
                output += f"\n\tID: `{k}`\n"
        else:
            output = "There are no Pilgrimages!"

    await ctx.send(output)

    print(f"{ctx.author} has run command list in #{ctx.channel}")


@client.command(name="award")
async def award(ctx, pid, *, member: discord.Member):
    get_db(ctx.guild.id).award(pid, member)
    await ctx.send("Might've worked. Who knows.")


@client.command(name="revoke")
async def revoke(ctx, pid, *, member: discord.Member):
    if pid == "-all":
        get_db(ctx.guild.id).revoke_all(member)
        await ctx.send("Maybe every pilgrimage was revoked.")
    else:
        get_db(ctx.guild.id).revoke(pid, member)
        await ctx.send("If you're lucky that pilgrimage was revoked.")




client.run(TOKEN)