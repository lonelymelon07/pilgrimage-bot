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

    print(f"{ctx.author} has run command 'init' in #{ctx.channel}")


@client.command(name="add")
async def add_pilgrimage(ctx, pid:str, score:int, *, display_name:str=""):
    """
    Adds a pilgrimage
    <pid> (pilgrimage ID) must contain only alphanumberic characters and underscores, cannot start with a number, and cannot be longer than 63 characters
    <score> any integer where -32728 < x < 32728
    <display_name> a string no longer than 127 characters. If none defaults to <pid>
    """
    if not pid.isidentifier(): # Ensures that `pid` is a valid identifier
        await ctx.send("ID must contain only alphanumeric characters and underscores, and cannot start with a number!")
        return

    # If there was no display name, we will set it to the id
    if not display_name:
        display_name = pid

    get_db(ctx.guild.id).add_pilg(pid, score, display_name)

    await ctx.send(f"Pilgrimage **{display_name}** created!\nScore: {score}\nID: `{pid}`")

    print(f"{ctx.author} has run command 'add' in #{ctx.channel}")


@client.command(name="remove", aliases=["rm", "delete", "del"])
async def remove_pilgrimage(ctx, pid:str):
    """
    Removes an existing pilgrimage
    <pid> the pilgrimage ID
    """

    get_db(ctx.guild.id).rm_pilg(pid)
    
    await ctx.send("Deleted the pilgrimage")

    print(f"{ctx.author} has run command 'remove' in #{ctx.channel}")
        

@client.command(name="list")
async def list_pilgrimages(ctx):
    """Lists all pilgrimages"""
    pilgs = get_db(ctx.guild.id).list_pilgs()  # List of tuples in form [(pid, display_name, score), ...]
    output = ""

    for pid, dn, score in pilgs:
        output += f"{dn}:"
        output += f"\n\tScore: {score}"
        output += f"\n\tID: `{pid}`\n"

    await ctx.send(output)

    print(f"{ctx.author} has run command 'list' in #{ctx.channel}")


@client.command(name="award")
async def award(ctx, pid, *, member: discord.Member):
    """
    Awards pilgrimage <pid> to <member>
    """
    
    get_db(ctx.guild.id).award(pid, member)
    await ctx.send("Might've worked. Who knows.")

    print(f"{ctx.author} has run command 'award' in #{ctx.channel}")


@client.command(name="revoke")
async def revoke(ctx, pid, *, member: discord.Member):
    """
    Revokes pilgrimage <pid> from <member>
    '-all' in place of <pid> will revoke all pilgrimages 
    """
    if pid == "-all":
        get_db(ctx.guild.id).revoke_all(member)
        await ctx.send("Maybe every pilgrimage was revoked.")
    else:
        get_db(ctx.guild.id).revoke(pid, member)
        await ctx.send("If you're lucky that pilgrimage was revoked.")

    print(f"{ctx.author} has run command 'revoke' in #{ctx.channel}")


@client.command(name="user")
async def user(ctx, *, member:discord.Member=None):
    """Lists all pilgrimages for a certain user.
    If [user] is left will default to current user"""
    if member is None:
        member = ctx.author

    pilgs = get_db(ctx.guild.id).get_member(member)

    output = ""
    total_score = 0
    for _, dn, score in pilgs:
        output += f"{dn}: {score}\n"
        total_score += score

    output += f"\nTotal: {total_score}"

    await ctx.send(output)

    print(f"{ctx.author} has run command 'user' in #{ctx.channel}")

client.run(TOKEN)