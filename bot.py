import discord
from discord.ext import commands
from util import JsonDB

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
async def add_pilgrimage(ctx, id:str, score:int, *, display_name:str=""):
    """Adds a pilgrimage"""
    async with ctx.typing():
        if not id.isidentifier(): # Ensures that `id` is a valid identifier
            await ctx.send("ID must contain only alphanumeric characters and underscores, and cannot start with a number!")
            return

        # If there was no display name, we will set it to the id
        if not display_name:
            display_name = id

        JsonDB.add_pilgrimage(ctx.guild, id, score, display_name)

        await ctx.send(f"Pilgrimage **{display_name}** created!\nScore: {score}\nID: `{id}`")

    print(f"{ctx.author} has run command add in #{ctx.channel}")


@client.command(name="remove",aliases=["rm", "delete", "del"])
async def remove_pilgrimage(ctx, id:str):
    """Removes an existing pilgrimage"""
    async with ctx.typing():
        success = JsonDB.remove_pilgrimage(ctx.guild, id)
        # Success: True/False based on whether it managed to delete the pilgrimage
        if success:
            await ctx.send(f"Pilgrimage `{id}` was removed!")
        else:
            await ctx.send(f"No pilrimage with ID `{id}` was found!")
            

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
async def award(ctx, id, *, member: discord.Member):
    success = JsonDB.add_pilgrimage_to_member(ctx.guild, id, member)
    if success == 0:
        await ctx.send(f"**{member}** has been awarded the {JsonDB.get_pilgrimage_display_name(ctx.guild, id)} pilgrimage")
    elif success == -1:
        await ctx.send("Nothing changed. The user already has that pilgrimage!")
    elif success == -2:
        await ctx.send(f"The Pilgrimage with ID `{id}` does not exist!")


@client.command(name="revoke")
async def revoke(ctx, id, *, member: discord.Member):
    if id == "-all":
        success = JsonDB.remove_all_pilgrimages_from_user(ctx.guild, member)
        if success == 0:
            await ctx.send(f"Revoked all pilgrimages from the user")
        else:
            await ctx.send(f"Nothing changed. The user does not have any pilgrimages.")
    else:
        success = JsonDB.remove_pilgrimage_from_user(ctx.guild, id, member)
        if success == 0:
            await ctx.send(f"User no longer has the `{id}` pilgrimage")
        else:
            await ctx.send(f"Nothing changed. The user did not have that pilgrimage.")


client.run(TOKEN)