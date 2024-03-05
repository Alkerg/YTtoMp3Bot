# Importing packages
import discord
import os
import asyncio
from discord.errors import HTTPException
from discord.ext import commands
from discord import app_commands, File
from pytube import YouTube, exceptions
from pytz import timezone
from datetime import datetime

# Constants
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_VERSION = 1.0
TZ = timezone("America/Lima")

# Set up
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    description="Hello, i'll help you to download YT videos in mp3/mp4 format",
    intents=intents)

# Commands
@bot.hybrid_command(name="mp3",
                    with_app_command=True,
                    description="Download a YT video in mp3 format")
@app_commands.describe(url="URL video: ")
async def mp3(ctx, *, url: str):

    await ctx.defer()
    await asyncio.sleep(3)
    
    try:
        #Youtbe Object
        yt = YouTube(url)

        # Extract only audio
        video = yt.streams.filter(only_audio=True).first()
        
    except exceptions.RegexMatchError:
        await ctx.send("Invalid URL") 
        return

    # Download the file
    out_file = video.download(output_path='')

    # Save the file
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    
    try:
        # Send result
        await ctx.send(file=File(new_file))
        os.remove(new_file)
        
    except HTTPException as e:
        if e.code == 40005:
            await ctx.send("Audio size is too large to send via Discord")
            os.remove(new_file)
        else:
            await ctx.send("Unhandled error: " + e.text)
        


@bot.hybrid_command(name="mp4",
                    with_app_command=True,
                    description="Download a YT video in mp4 format")
@app_commands.describe(url="URL video: ")
async def mp4(ctx, *, url: str):
    
    await ctx.defer()
    await asyncio.sleep(3)
    
    try:
        #Youtbe Object
        yt = YouTube(url) 
        
        # Download the video
        yt = yt.streams.get_highest_resolution()
        yt.download(output_path='')
        
        # Define path
        new_file = './' + yt.title + '.mp4'
        
    except exceptions.RegexMatchError:
        await ctx.send("Invalid URL") 
        return
    
    try:    
        # Send result
        await ctx.send(file=File(new_file))
        os.remove(new_file)
    except HTTPException as e:
        if e.code == 40005:
            await ctx.send("Video size is too large to send via Discord")
            os.remove(new_file)
        else:
            await ctx.send("Unhandled error: " + e.text)
    

# Events
@bot.event
async def on_ready():
    print("-----------------------------")
    print("YTtoMP3Bot is ready")
    print(datetime.now(TZ).strftime("%d-%m-%Y"))
    print(datetime.now(TZ).strftime("%I:%M %p"))

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as error:
        print(error)
        print("-----------------------------")
  
    await bot.change_presence(activity=discord.Game(name="videos", type=1))


# Endpoint
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
