import os
import discord
from discord import FFmpegPCMAudio
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from datetime import datetime 
from datetime import timezone
from datetime import timedelta
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

number_emojis = [
    "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣",
    "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
]

# judged_messages now stores message_id: channel_id
judged_messages = {}

# judging channels per guild {guild_id: channel_id}
judging_channels = {}
JUDGING_CHANNEL_FILE = "judging_channels.json"

# cutoff timestamps per judging channel {channel_id: iso_timestamp_string}
cutoff_timestamps = {}
CUTOFF_FILE = "cutoffs.json"

average_channels = {}
AVERAGE_FILE = "average_channels.json"

bot.launch_time = None



def save_average_channels():
    with open(AVERAGE_FILE, "w") as c:
        json.dump(average_channels, c)

def load_average_channels():
    global average_channels
    if os.path.exists(AVERAGE_FILE):
        with open(AVERAGE_FILE, "r") as f:
            try:
                average_channels = json.load(f)
                average_channels = {int(k): int(v) for k, v in average_channels.items()}
                print(f"Loaded average channels: {average_channels}")
            except Exception as e:
                print(f"Error loading average channels: {e}")
                average_channels = {}

def save_judging_channels():
    with open(JUDGING_CHANNEL_FILE, "w") as f:
        json.dump(judging_channels, f)

def load_judging_channels():
    global judging_channels
    if os.path.exists(JUDGING_CHANNEL_FILE):
        with open(JUDGING_CHANNEL_FILE, "r") as f:
            try:
                judging_channels = json.load(f)
                judging_channels = {int(k): int(v) for k, v in judging_channels.items()}
                print(f"Loaded judging channels: {judging_channels}")
            except Exception as e:
                print(f"Error loading judging channels: {e}")
                judging_channels = {}

def save_cutoffs():
    with open(CUTOFF_FILE, "w") as f:
        json.dump(cutoff_timestamps, f)

def load_cutoffs():
    global cutoff_timestamps
    if os.path.exists(CUTOFF_FILE):
        with open(CUTOFF_FILE, "r") as f:
            try:
                cutoff_timestamps = json.load(f)
                print(f"Loaded cutoff timestamps: {cutoff_timestamps}")
            except Exception as e:
                print(f"Error loading cutoff timestamps: {e}")
                cutoff_timestamps = {}

@bot.event
async def on_ready():
    global launch_time
    launch_time = datetime.now()
    launch_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Bot is online! Started at {launch_time}")
    uptime = 0

    while True:
        await asyncio.sleep(1)
        uptime + 1 

@bot.command()
async def check_channel(ctx):
    await ctx.send(f"This command was sent in #{ctx.channel.name} (ID: {ctx.channel.id}).")



@bot.command()
async def bothelp(ctx):
    await ctx.send(
        f"Here is a list of all commands and functions.\n\n"
        f"!bothelp: Shows this message.\n"
        f"!set_judging_channel: Sets the judging channel for this server.\n"
        f"!view_judging_channel: Shows the currently set judging channel for this server.\n"
        f"!judge: Adds reactions 0-10 to the message.\n"
        f"!start_new_judging: Sets cutoff timestamp for the current judging channel.\n"
        f"!set_average_channel: Sets the channel where the !average command can be used. Used to avoid spoliers.\n"
        f"!view_average_channel: Shows the currently set average channel for this server.\n"
        f"!average: Shows average scores for judged messages.\n"
        f"!uptime: Shows how long the bot has been up in its current session."
        f"!chillwithivan: Chill with Ivan. \n"
        f"!freedom: FREEDOM.\n"
        f"!bunny: Bugs bunny!\n"
        f"!teto: my sins are innumerable and the voices grow louder\n"
        f"!thirsty: thirst"
    )

@bot.command()
async def uptime(ctx):
    if launch_time is None:
        await ctx.send("I just started, no uptime yet!")
        return

    now = datetime.now()
    delta = now - launch_time

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    await ctx.send(f"⏱ Uptime: {uptime_str}")





@bot.command()
async def bunny(ctx):
    await ctx.send(file=discord.File(r"D:\Desktop\Memes\ScreenRecording_07-04-2025_15-10-28_1.mov"))

@bot.command()
async def chillwithivan(ctx):
    await ctx.send("https://tenor.com/view/stalker-gif-22322541")

@bot.command()
async def freedom(ctx):
    await ctx.send("OH YEAH? LAND OF THE FREE? THEN WHY CAN'T I RINSE MY BALLS IN THE BURGER KING SODA DISPENSER?!?")

@bot.command()
async def set_average_channel(ctx):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("You must have the manage channels permission to set a channel.")
        return

    """Set average channel for this server and save persistently."""
    guild_id = ctx.guild.id
    average_channels[guild_id] = ctx.channel.id
    save_average_channels()
    await ctx.send(f"Average channel set to: #{ctx.channel.name}")

@bot.command()
async def set_judging_channel(ctx):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("You must have the manage channels permission to set a channel.")
        return
    """Set judging channel for this server and save persistently."""
    guild_id = ctx.guild.id
    judging_channels[guild_id] = ctx.channel.id
    save_judging_channels()
    await ctx.send(f"Judging channel set to: #{ctx.channel.name}")

@bot.command()
async def start_new_judging(ctx):
    """Set cutoff timestamp for the current channel (overwrites previous one)."""
    channel_id = ctx.channel.id
    timestamp = ctx.message.created_at.replace(tzinfo=timezone.utc).isoformat()
    # Overwrite the previous cutoff (no need to manually delete it)
    cutoff_timestamps[str(channel_id)] = timestamp
    save_cutoffs()
    await ctx.send(f"Cutoff set for #{ctx.channel.name}: {timestamp}")


@bot.command()
async def judge(ctx):
    """Add 0-10 reactions and track the message with its channel."""
    message = ctx.message
    for emoji in number_emojis:
        await message.add_reaction(emoji)
    judged_messages[message.id] = message.channel.id

@bot.command(name="average")
async def average(ctx):
    """Average scores for judged messages from this server's judging channel, respecting cutoff."""
    emoji_to_value = {emoji: i for i, emoji in enumerate(number_emojis)}
    
    guild_id = ctx.guild.id
    average_channel_id = average_channels.get(guild_id)

    if average_channel_id is None:
        await ctx.send(f"A average channel is not set. Use !set_average_channel to set one.")
        return
    
    if ctx.channel.id != average_channel_id:
        await ctx.send(f"This is not the set average channel.")
        return
    

    if not judged_messages:
        await ctx.send("No judged messages found yet.")
        return

    guild_id = ctx.guild.id
    judging_channel_id = judging_channels.get(guild_id)

    if judging_channel_id is None:
        await ctx.send("Judging channel not set for this server. Use !set_judging_channel in the correct channel.")
        return

    cutoff_timestamp_str = cutoff_timestamps.get(str(judging_channel_id))
    if cutoff_timestamp_str:
        from dateutil.parser import isoparse
        cutoff_timestamp = isoparse(cutoff_timestamp_str)
        cutoff_msg = f"Only including judged messages after {cutoff_timestamp_str}."
    else:
        cutoff_timestamp = None
        cutoff_msg = "No cutoff set; averaging all judged messages."

    submissions = []

    await ctx.send("Averaging scores...")

    for msg_id, chan_id in judged_messages.items():
        
        if ctx.channel.id == average_channels:
            continue
        # Only messages from the judging channel
        if chan_id != judging_channel_id:
            continue

        try:
            channel = bot.get_channel(chan_id)
            if channel is None:
                continue
            message = await channel.fetch_message(msg_id)
        except Exception:
            continue

        if cutoff_timestamp and message.created_at.replace(tzinfo=timezone.utc) <= cutoff_timestamp:
            continue

        total_weighted = 0
        total_count = 0

        for reaction in message.reactions:
            emoji = str(reaction.emoji)
            value = emoji_to_value.get(emoji)
            if value is None:
                continue

            users = [user async for user in reaction.users()]
            count = sum(1 for user in users if user.id != bot.user.id)
            total_weighted += value * count
            total_count += count


        if total_count == 0:
            avg_result = "No valid reactions"
        else:
            average_score = total_weighted / total_count
            avg_result = f"{average_score:.2f}"

        if message.guild:
            link = f"https://discord.com/channels/{message.guild.id}/{channel.id}/{message.id}"
            submissions.append(f"[Submission #{len(submissions)+1}]({link}): {avg_result}")
        else:
            submissions.append(f"[Submission #{len(submissions)+1}]: {avg_result}")

    if not submissions:
        await ctx.send(f"No valid judged messages found.\n{cutoff_msg}")
        return

    output = "\n".join(submissions)
    await ctx.send(f"Average scores:\n{output}\n\n{cutoff_msg}")

@bot.command()
async def view_judging_channel(ctx):
    """Shows the current judging channel set for this server."""
    guild_id = ctx.guild.id
    channel_id = judging_channels.get(guild_id)
    if channel_id is None:
        await ctx.send("No judging channel set for this server. Use !set_judging_channel in the desired channel.")
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send("The judging channel set for this server no longer exists.")
        return

    await ctx.send(f"The judging channel for this server is set to: #{channel.name}")

@bot.command()
async def view_average_channel(ctx):
    """Shows the current average channel set for this server."""
    guild_id = ctx.guild.id
    channel_id = average_channels.get(guild_id)
    if channel_id is None:
        await ctx.send("No average channel set for this server. Use !set_average_channel in the desired channel.")
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send("The average channel set for this server no longer exists.")
        return

    await ctx.send(f"The average channel for this server is set to: #{channel.name}")

@bot.command()
async def teto(ctx):
     await ctx.send("https://tenor.com/view/teto-kasane-teto-teto-plush-kasane-teto-plush-crush-it-gif-16166927453889012815")


@bot.command()
async def thirsty(ctx):
    
    embed = discord.Embed(
        title="Here's some water.",
        description="Now drink.",
        color=discord.Color.blue(),
        url="https://en.wikipedia.org/wiki/Flint_water_crisis"
    )
    await ctx.send(embed=embed)

motion_users = set()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id

    # First trigger phrase
    if message.content.lower() == "judgebot, do you have motion?":
        await message.channel.send("https://tenor.com/view/rich-off-airpods-richoffairpods-stack-band-bandforband-gif-4351078540525453133")
        motion_users.add(user_id)

    # Second trigger phrase, only if user sent the first
    elif message.content.lower() == "can you show me your motion... in person?" and user_id in motion_users:
        await message.channel.send("https://cdn.discordapp.com/attachments/1243324240598663291/1402837043800838144/IMG_3819.png?ex=68955d4e&is=68940bce&hm=e875a49c8e4a3c1177cf7a7f713715187db8c15be9029e04b0a85e268ebbf442&")
        motion_users.remove(user_id)

    await bot.process_commands(message) 
    


# Load persisted data on startup
load_judging_channels()
load_average_channels()
load_cutoffs()

bot.run(TOKEN)
