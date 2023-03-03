import os
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
client_id = open('C:/Users/Luke/Documents/Blu3T1ger/reddit/client_id.txt')
client_secret = open(
    'C:/Users/Luke/Documents/Blu3T1ger/reddit/client_secret.txt')
token = open('C:/Users/Luke/Documents/Blu3T1ger/discord/token.txt')

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


@client.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@client.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


# START OF MUSIC

ytdl_format_options = {  # format options for our downloader
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

# loads our format options dicitonary
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):  # set our volume
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.ffmpeg_options = ffmpeg_options

        self.vc = None

    def search_yt(self, searchquery):
        try:
            info = ytdl.extract_info('ytsearch:%s' %
                                     searchquery, download=False)['entries'][0]
        except Exception:
            return False
        return {'source': info['formats'[0]['url']], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:  # if something in queue
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegAudio(
                m_url, **self.ffmpeg_options), after=lambda e: self.play_next)
        else:
            self.is_playing = False  # Otherwise we aren't playing anything

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc == await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("Could not connect to voice channel!")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegAudio(
                m_url, **self.ffmpeg_options), after=lambda e: self.play_next)
        else:
            self.is_playing = False

    @client.command(name='play', aliases=['pl'])
    async def play(self, ctx, *args):
        query = "".join(args)  # using arguments from command call
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("You are not in a voice channel!!!!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Error playing song, please try again.")
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(ctx)

    @client.command(name='pause')
    async def pause(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @client.command(name='stop')
    async def stop(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @client.command(aliases=['dc'])
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()


@client.command()
async def poker(ctx, *, gameHandler):

    if gameHandler == "start":
        cards = ["♠️1", "♠️2", "♠️3", "♠️4", "♠️5", "♠️6", "♠️7", "♠️8", "♠️9", "♠️10", "♠️11", "♠️12", "♠️13",
                 "♥️1", "♥️2", "♥️3", "♥️4", "♥️5", "♥️6", "♥️7", "♥️8", "♥️9", "♥️10", "♥️11", "♥️12", "♥️13",
                 "♦️1", "♦️2", "♦️3", "♦️4", "♦️5", "♦️6", "♦️7", "♦️8", "♦️9", "♦️10", "♦️11", "♦️12", "♦️13",
                 "♣️1", "♣️2", "♣️3", "♣️4", "♣️5", "♣️6", "♣️7", "♣️8", "♣️9", "♣️10", "♣️11", "♣️12", "♣️13"]  # array of deck of cards
        deck = {"♠️1": 1, "♠️2": 2, "♠️3": 3, "♠️4": 4, "♠️5": 5, "♠️6": 6, "♠️7": 7, "♠️8": 8, "♠️9": 9, "♠️10": 10, "♠️11": 11, "♠️12": 12, "♠️13": 13,
                "♥️1": 1, "♥️2": 2, "♥️3": 3, "♥️4": 4, "♥️5": 5, "♥️6": 6, "♥️7": 7, "♥️8": 8, "♥️9": 9, "♥️10": 10, "♥️11": 11, "♥️12": 12, "♥️13": 13,
                "♦️1": 1, "♦️2": 2, "♦️3": 3, "♦️4": 4, "♦️5": 5, "♦️6": 6, "♦️7": 7, "♦️8": 8, "♦️9": 9, "♦️10": 10, "♦️11": 11, "♦️12": 12, "♦️13": 13,
                "♣️1": 1, "♣️2": 2, "♣️3": 3, "♣️4": 4, "♣️5": 5, "♣️6": 6, "♣️7": 7, "♣️8": 8, "♣️9": 9, "♣️10": 10, "♣️11": 11, "♣️12": 12, "♣️13": 13}
        gameStart = True
        round = 1
        money = 2500.00
        # random  card from deck
        playerCard1 = deck[random.randint(0, len(cards)-1)]
        # when we take a card from a deck, we a re removing the card
        deck.remove(playerCard1)
        playerCard2 = cards[random.randint(0, len(cards)-1)]
        cards.remove(playerCard2)
        await ctx.send(f"Your cards are `{playerCard1}` and `{playerCard2}`")
        while gameStart == True:
            if round == 1:
                break
    else:
        await ctx.send("Error")

        # Runs the token given to start up the bot
client.run(token.read())
