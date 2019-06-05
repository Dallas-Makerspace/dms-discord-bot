#!/usr/bin/python3.7 -u
import io
import typing
import asyncio
import aiohttp
from functions import *
from discord.ext import commands
from datetime import datetime

bot = commands.Bot(command_prefix="!", case_insensitive=True, help_command=None)

def get_command_help(command):
    help = f"`{bot.command_prefix}{command.name} "
    for alias in sorted(command.aliases):
        help = help + f"or {bot.command_prefix}{alias} "
    if command.signature != "":
        help = help + f"{command.signature} "
    help = help + f"` - {command.help}"
    return help

def has_role(member, role_name):
    for role in member.roles:
        if role.name.lower() == role_name.lower():
            return True
    return False

def get_guild():
    guild_id = config["discord"]["guild_id"]
    return bot.get_guild(guild_id)

def get_channel(name):
    for channel in get_guild().channels:
        if channel.name == name:
            return channel
    return None

def get_category(name):
    for category in get_guild().categories:
        if category.name.lower() == name.lower():
            return category
    return None

def get_channel_by_topic(topic):
    for channel in get_guild().text_channels:
        if channel.topic == topic:
            return channel
    return None

def get_role(name):
    for role in get_guild().roles:
        if role.name.lower() == name.lower():
            return role
    return None

def get_members_by_role(name):
    return get_role(name).members

@asyncio.coroutine
async def monitor_deletions():
    guild = get_guild()
    waifu_audit_log = {}
    action = discord.AuditLogAction.message_delete
    async for entry in guild.audit_logs(action=action, limit=25):
        if entry.id not in waifu_audit_log:
            if seconds_since(entry.created_at) < 3600:
                waifu_audit_log[entry.id] = entry
    while True:
        message = await bot.wait_for("message_delete")
        deleted_by = message.author
        author = message.author
        async for entry in guild.audit_logs(action=action, limit=5):
            if entry.extra.channel == message.channel:
                if entry.id not in waifu_audit_log:
                    if seconds_since(entry.created_at) < 60:
                        waifu_audit_log[entry.id] = entry
                        deleted_by = entry.user
                elif waifu_audit_log[entry.id].extra.count != entry.extra.count:
                    waifu_audit_log[entry.id] = entry
                    deleted_by = entry.user
                else:
                    if seconds_since(waifu_audit_log[entry.id].created_at) > 86400:
                        del waifu_audit_log[entry.id]
        if author == bot.user and deleted_by == bot.user:
            continue
        timestamp = message.created_at.strftime("%m/%d/%Y %H:%M")
        title = f"ID: {message.id}"
        description = f"Author: {author.mention}\nDeleted by: {deleted_by.mention}*\nChannel: {message.channel.mention}\nUTC: {timestamp}"
        embed = discord.Embed(title=title, description=description, color=discord.Color.red())
        deleted_embeds = message.embeds
        if len(message.content) > 0:
            value = f"\"{message.content}\""
            embed.add_field(name="Message", value=value, inline=False)
        if len(message.attachments) > 0:
            name = "Attachments"
            value = ""
            for attachment in message.attachments:
                value = value + "<{}>\n".format(attachment.proxy_url)
            embed.add_field(name=name, value=value, inline=False)
        if len(message.embeds) > 0:
            name = "Embeds"
            value = f"{len(message.embeds)} found. See below:"
            embed.add_field(name=name, value=value, inline=False)
        channel = get_channel("deleted_text")
        await channel.send(embed=embed)
        for index, embed in enumerate(deleted_embeds):
            embed.color = waifu_pink
            reply = f"**Embed {index + 1} of {len(deleted_embeds)}**"
            await channel.send(reply, embed=embed)

@bot.event
async def on_ready():
    log.info(f"Logged on as {bot.user}")
    loop = asyncio.get_event_loop()
    monitor_deletions_task = loop.create_task(monitor_deletions())

@bot.event
async def on_command_error(ctx, error):
    error_text = str(error)
    if isinstance(error, commands.UserInputError):
        if error_text != "":
            if error_text[-1] != ".":
                error_text = error_text + "."
        error_text = sentence_case(error_text)
        error_text = error_text + "\n" + get_command_help(ctx.command)
        reply = f"ERROR: {ctx.author.mention}, invalid syntax.\n{error_text}"
        await ctx.send(reply)
    elif isinstance(error, commands.MissingRole):
        reply = f"ERROR: {ctx.author.mention}, missing role."
        await ctx.send(reply)
    elif isinstance(error, commands.NoPrivateMessage):
        reply = f"ERROR: {ctx.author.mention}, bad channel."
        await ctx.send(reply)
    elif isinstance(error, commands.errors.CommandNotFound):
        reply = f"ERROR: {ctx.author.mention}, invalid command. Maybe try `!about`."
        await ctx.send(reply)
    elif isinstance(error, commands.errors.CommandInvokeError):
        raise error.original
    log_msg = f"[{ctx.author}] - [{ctx.channel}]\n[{error.__class__}]\n{ctx.message.content}"
    log.error(log_msg)
    return

@bot.command(aliases=["info"])
@commands.guild_only()
async def about(ctx):
    """Display this help message."""
    reply = "I understand the following commands:\n\n"
    for command in sorted(bot.commands, key=lambda x: x.name):
        if not command.hidden:
            reply = reply + get_command_help(command) + "\n"
    reply = reply + "\nMy source code is available on GitHub: https://github.com/Dallas-Makerspace/dms-discord-bot"
    await ctx.send(reply)

@bot.command()
@commands.guild_only()
async def members(ctx):
    """Show the total number of active DMS members."""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://accounts.dallasmakerspace.org/member_count.php') as resp:
            if resp.status != 200:
                reply = f"Error {resp.status}: I cannot access that info right now."
                await ctx.send(reply)
                return
            total = (await resp.json(content_type='text/html'))['total']
            reply = f"There are currently {total} members."
            await ctx.send(reply)
    return

@bot.command()
@commands.guild_only()
async def magic8ball(ctx, question: str):
    """Ask the magic 8 ball a question."""
    answer = random.choice(strings['eight_ball'])
    reply = f"{ctx.author.mention}, the magic 8 ball has spoken: \"{answer}\"."
    await ctx.send(reply)
    return

@bot.command(name="random")
@commands.guild_only()
async def _random(ctx):
    """Request a random number, chosen by fair dice roll."""
    await ctx.send(f"{ctx.author.mention}: 4")
    def check(answer):
        if answer.channel == ctx.channel:
            is_not = ["n't", "not", "no", "crypto"]
            for word in is_not:
                if (word in answer.content.lower() and "random" in answer.content.lower()) or answer.content.lower().startswith("!random"):
                    return True
        return False
    try:
        answer = await bot.wait_for("message", timeout=300, check=check)
        if answer.content.lower().startswith("!random"):
            return
        reply = f"{answer.author.mention}, I disagree:\nhttps://xkcd.com/221/"
        await ctx.send(reply)
        return
    except asyncio.TimeoutError:
        return

@bot.command(hidden=True)
@commands.has_role("nerds")
@commands.guild_only()
async def die(ctx):
    """Kill my currently running instance. I won't forget this."""
    reply = random.choice(strings['last_words'])
    await ctx.send(reply)
    exit(0)
    return

token = config["discord"]["token"]
bot.run(token)
