import discord
import random
import praw
import time
import youtube_dl
import asyncio
import urllib.request
from bs4 import BeautifulSoup
from discord.ext import commands

client = commands.Bot(command_prefix=',')  # Sets the command prefix
client_id = open('./reddit/client_id.txt')
client_secret = open('./reddit/client_secret.txt')
token = open('./discord/token.txt')

redit = praw.Reddit(client_id=client_id.read(),
                    client_secret=client_secret.read(),
                    user_agent='python bot')  # Gives the personal user app from reddit for the needed info for reddit. I also used 'redit' instead of reddit so I could use reddit for the command without returning an error.


@client.event
async def on_ready():
    # Writes in the terminal that it is successfully connected
    print("Connected!")


@client.event
async def on_member_join(member):
    # Displays the message in console when someone joins
    print(f"{member} has joined the server!")


@client.event
async def on_member_remove(member):
    # Displays the message in console when someone leaves
    print(f"{member} has left the server!")


@client.command()
async def ping(ctx):  # Commands need context as there input
    # Responds with context.send because it sends the message with the given context of the message
    await ctx.send("Success.")


# The aliases = makes it so the command can also use these as input.
@client.command(aliases=['8ball', 'magic8ball'])
# I'm taking multiple arguments here with the star seperating and also taking in a question
async def _8ball(ctx, *, question):
    responses = ["It is certain.",
                 "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
                 "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
                 "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
                 "My sources say no.", "Outlook not so good.", "Very doubtful."]  # This is a list of common 8 ball phrases
    # The random.choice outputs a random choice from the list
    await ctx.send(f"{random.choice(responses)}")


# Has the alias delete so people can also just use delete for the command.
@client.command(aliases=['delete'])
# Takes the amount argument and, if no argument is given, will just delete 1 message by default
async def clear(ctx, amount=1):
    # Bot says its deleting that amount of messages
    await ctx.send(f"Deleting `{amount}` messages.")
    # Using time, the bot waits for 1 second so the user can read the message.
    time.sleep(1)
    # Now the bot deletes all messages given + 2 because we also want to delete the message the bot and user sent.
    await ctx.channel.purge(limit=amount + 2)


# Also takes alias subreddit because this just makes sense
@client.command(aliases=['subreddit'])
async def reddit(ctx, *, subreddit):  # Input is subreddit
    # Looks at the subreddit's hot section
    submissions = redit.subreddit(subreddit).hot()
    post = random.randint(1, 25)  # Takes a random post from the current top 25
    for x in range(0, post):
        submission = next(x for x in submissions if not x.stickied)

    await ctx.send(submission.url)  # Sends the post url


@client.command(aliases=['nsfwgif'])
async def porngif(ctx, posts=1):
    while posts > 5:
        await ctx.send("The number of posts is too high, please input a number below 5.")
        return
    subreddits = ['NSFW_GIF', 'nsfw_gifs',
                  'The_Best_NSFW_GIFS', 'nsfwhardcore']
    # Looks at the subreddit's hot section
    submissions = redit.subreddit(random.choice(subreddits)).hot()
    # A for loop to run through how many images to be sent
    for postcount in range(0, posts):
        # Takes a random post from the current top 25
        post = random.randint(1, 25)
        for x in range(0, post):
            submission = next(x for x in submissions if not x.stickied)

        await ctx.send(submission.url)


@client.command()
# This command is exclusively used for testing to get the right url to play music.
async def url(ctx, *, search):
    search = search.split(" ")
    query = urllib.parse.quote(str(search))
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}, limit=1):
        url = 'https://www.youtube.com' + vid['href']
        await ctx.send(url)


@client.command()
# With no parameters given, it will automatically use the amount of 10 messages and the word nuked
async def nuke(ctx, amount=10, *, word="nuked"):
    # A for loop in range of the amount of messages sent
    for messagecount in range(0, amount):
        await ctx.send(word)  # Sends the word
        time.sleep(.1)  # Sleeps for .1s to not go too fast.


# START OF MUSIC

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.command(aliases=['pl'])
    async def play(self, ctx, *, searchquery):
        searchquery = searchquery.split(" ")
        query = urllib.parse.quote(searchquery)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}, limit=1):
            url = 'https://www.youtube.com' + vid['href']
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(
                f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @client.command(aliases=['dc'])
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


# Runs the token given to start up the bot
client.run(token.read())
