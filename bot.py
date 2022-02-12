import discord
from discord.ext import commands
import json

from errors import *
from db import get_db
from converters import idstr, smallint, str127

with open("config.json") as f:
    g = json.load(f)
    TOKEN = g["token"]
    ADMIN_ROLE_ID = g["admin_role"]


client = commands.Bot(command_prefix = ";")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_command_error(ctx, error):
    output = ":no_entry_sign:  **Oops! An error occurred.**\n"
    if isinstance(error, commands.CommandInvokeError):
        e = error.original
    
        if isinstance(e, DatabaseError):
            output += f"```DataError: {e}```"
        else:
            output += "```Unknown Error```"
    elif isinstance(error, commands.UserInputError):
        output += f"```UserInputError: {error}```"
    elif isinstance(error, commands.CheckFailure):
        output += f"```PermissionsFaliure: {error}```"
    else:
        output += "```Unknown Error```"

    print(f"[Command Raised an Error]: {error}")

    await ctx.send(output)
            

@client.command(name="add", aliases=["new"])
@commands.has_role(ADMIN_ROLE_ID)
async def add_pilgrimage(ctx, pid:str, score:int, *, display_name:str=""):
    """
    Adds a pilgrimage
    <pid> (pilgrimage ID) must contain only alphanumberic characters and underscores, cannot start with a number, and cannot be longer than 63 characters
    <score> any integer where -32728 < x < 32728
    <display_name> a string no longer than 127 characters. If none defaults to <pid>
    """

    pid = idstr(pid)
    score = smallint(score)
    display_name = str127(display_name)

    # If there was no display name, we will set it to the id
    if not display_name:
        display_name = pid

    tdb = get_db(ctx.guild.id)

    if not tdb.pilg_exists(pid):
        tdb.add_pilg(pid, score, display_name)
        await ctx.send(f"Pilgrimage **{display_name}** created!\nScore: {score}\nID: `{pid}`")
    else:
        raise PilgrimageAlreadyExistsError(f"Pilgrimage {pid} already exists!")

    print(f"{ctx.author} has run command 'add' in #{ctx.channel}")


@client.command(name="remove", aliases=["rm", "delete", "del"])
@commands.has_role(ADMIN_ROLE_ID)
async def remove_pilgrimage(ctx, pid:str):
    """
    Removes an existing pilgrimage
    <pid> the pilgrimage ID
    """

    tdb = get_db(ctx.guild.id)

    if tdb.pilg_exists:
        get_db(ctx.guild.id).rm_pilg(pid)
        await ctx.send("Deleted the pilgrimage")
    else:
        raise PilgrimageNotFoundError(f"Pilgrimage {pid} does not exist!")

    print(f"{ctx.author} has run command 'remove' in #{ctx.channel}")
        

@client.command(name="list", aliases=["pilgs", "pilgrimages"])
async def list_pilgrimages(ctx):
    """Lists all pilgrimages"""
    pilgs = get_db(ctx.guild.id).list_pilgs()  # List of tuples in form [(pid, display_name, score), ...]
    output = ""

    if len(pilgs):
        for pid, dn, score in pilgs:
            output += f"{dn}:"
            output += f"\n\tScore: {score}"
            output += f"\n\tID: `{pid}`\n"
    else:
        output += "There are no pilgrimages!"

    await ctx.send(output)

    print(f"{ctx.author} has run command 'list' in #{ctx.channel}")


@client.command(name="award", aliases=["awd"])
@commands.has_role(ADMIN_ROLE_ID)
async def award(ctx, pid:str, *, member: discord.Member):
    """
    Awards pilgrimage <pid> to <member>
    """
    
    tdb = get_db(ctx.guild.id)

    if tdb.pilg_exists(pid):
        if not tdb.member_has_pilg(pid, member):
            tdb.award(pid, member)
            await ctx.send(f"Gave the {pid} pilgrimage to {member}!")
        else:
            raise MemberHasPilgrimageError(f"{member} already has that pilgrimage")
    else:
        raise PilgrimageNotFoundError(f"Pilgrimage {pid} does not exist!")

    print(f"{ctx.author} has run command 'award' in #{ctx.channel}")


@client.command(name="revoke", aliases=["rv"])
@commands.has_role(ADMIN_ROLE_ID)
async def revoke(ctx, pid:str, *, member: discord.Member):
    """
    Revokes pilgrimage <pid> from <member>
    '-all' in place of <pid> will revoke all pilgrimages 
    """

    tdb = get_db(ctx.guild.id) # temp db

    if pid == "-all":
        if len(tdb.get_member(member)):
            tdb.revoke_all(member)
            await ctx.send(f"Revoked every pilgrimage from {member}")
        else:
            raise MemberHasNotPilgrimageError(f"Nothing changed; {member} has no pilgrimages")
    else:
        if tdb.member_has_pilg(pid, member):
            tdb(ctx.guild.id).revoke(pid, member)
            await ctx.send("If you're lucky that pilgrimage was revoked.")
        else:
            raise MemberHasNotPilgrimageError(f"Nothing changed; {member} does not have pilgrimage {pid}")

    print(f"{ctx.author} has run command 'revoke' in #{ctx.channel}")


@client.command(name="user", aliases=["member", "awards"])
async def user(ctx, *, member:discord.Member=None):
    """Lists all pilgrimages for a certain user.
    If [user] is left will default to current user"""
    if member is None:
        member = ctx.author

    # A list of pilgs, in form [(pid, display_name, score), ...]
    pilgs = get_db(ctx.guild.id).get_member(member)

    if len(pilgs) > 0:  # If this user actually has any pilgrimages
        output = ""
        total_score = 0
        for _, dn, score in pilgs:
            output += f"{dn}: {score}\n"
            total_score += score

        output += f"\nTotal: {total_score}"
    else:
        output = "That user has no pilgrimages."

    await ctx.send(output)

    print(f"{ctx.author} has run command 'user' in #{ctx.channel}")


client.run(TOKEN)