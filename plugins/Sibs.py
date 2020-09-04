import discord
from discord.ext.commands import Bot
from discord.ext import commands

import urllib
import argparse
import requests
import lxml
from bs4 import BeautifulSoup
from pymarkovchain import MarkovChain

import threading
import asyncio
import os

import twitter

import tweepy


class Sibs(commands.Cog):
    helpstring = []
    helpEmoji = '🇷🇺'
    twi = None
    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!history *number; Generate a markov seed from channel with number messages')
        self.helpstring.append('!!twit &handle *number ; Scrapes number tweets from handle\'s feed and builds markov seed')
        self.helpstring.append('!!scrape *url *start *end ; Scrape tumblr blog from start page to end page and build markov seed')
        self.helpstring.append('!!geneva *number *filename; Returns number of quotes from the given markov seed (g)')
        self.helpstring.append('!!list ; Lists all available markov seeds')
        secrets = {}
        with open('/home/pi/Botty/deps/twit_secrets.txt', 'r') as f:
            for l in f.readlines():
                d = l.replace('\n', '').split('----')
                secrets[d[0]] = d[1]

        self.twi = twitter.Api(consumer_key=secrets['ApiKey'],
                  consumer_secret=secrets['ApiKeySecret'],
                  access_token_key=secrets['AccessToken'],
                  access_token_secret=secrets['AccessTokenSecret'])



        auth = tweepy.OAuthHandler(secrets['ApiKey'], secrets['ApiKeySecret'])
        auth.set_access_token(secrets['AccessToken'], secrets['AccessTokenSecret'])
        self.twe = tweepy.API(auth, wait_on_rate_limit=True)

        self.twi.VerifyCredentials()
        
    @commands.command(pass_context=True)
    async def list(self, ctx):
        files = os.listdir('/home/pi/Botty/markov/')
        msg = []
        msg.append('```ini\n')
        for f in files:
            msg.append(f'[{f.replace(".markov","")}]')
        msg.append('\n```')
        await ctx.channel.send('\n'.join(msg))


    @commands.command(pass_context=True)
    async def geneva(self, ctx, number=1, filename=None, minlen=3, notags=False):
        try:
            NUMBER = int(number)
            minlen = int(minlen)
        except:
            await ctx.channel.send('Bad args')
            return
        if filename is None:
            filename = ctx.channel.name
        FILENAME = '/home/pi/Botty/markov/' + filename
        if '.markov' not in FILENAME:
            FILENAME += '.markov'
        if not os.path.exists(FILENAME):
            await ctx.channel.send('Could not find file')
            return
        try:
            BOT = MarkovChain(FILENAME)
        except: 
            print('Die i guess')

        VALID_SENTENCES = 0
        TIMEOUT = 0
        msg = []
        while VALID_SENTENCES < NUMBER:
            SENTENCE = BOT.generateString()
            TIMEOUT += 1
            if TIMEOUT > 1000:
                if(msg):
                    await ctx.channel.send('\n'.join(msg))
                else:
                    await ctx.channel.send('Markov file corrupt. Kill it')
                return

            if len(SENTENCE.split()) < minlen:
                continue
            VALID_SENTENCES += 1
            
            
            msg.append(SENTENCE)
            await asyncio.sleep(.01)
        await ctx.channel.send('\n'.join(msg))
    '''
            if not notags:
                try:
                    TAGS=BOT.generateStringWithSeed("#")
                    print(TAGS)
                    print(" --- ")
                except pymarkovchain.StringContinuationImpossibleError as e:
                    print("[FATAL] Your database does not have tag data.")
                    print("You can still generate posts without tags using --notags")
                    return
    '''


    @commands.command(pass_context=True)
    async def g(self, ctx, number=1, filename=None, minlen=3, notags=False):
        await geneva(ctx, number=1, filename=None, minlen=3, notags=False)

    @commands.command(pass_context=True)
    async def scrape(self, ctx, url, start=1, end=10, tag=None, notags=False, nohash=False, prune=False, debug=False):
        if tag == None:
            TARGET_URL = "https://{}.tumblr.com/page/".format(url)
            TARGET_FILE = "/home/pi/Botty/markov/{}.markov".format(url)
        else:
            TARGET_URL = "https://{}.tumblr.com/tagged/{}/page/"
            TARGET_URL = TARGET_URL.format(url, urllib.parse.quote(tag))
            TARGET_FILE = "/home/pi/Botty/markov/{}.{}.markov".format(url, urllib.parse.quote(tag))

        await ctx.channel.send('Scraping...')
        try:
            os.remove(TARGET_FILE)
        except OSError:
            pass
        CORPUS = await self.gen(TARGET_URL, start, end, tag, notags, nohash, prune, debug)
        #print("Generating database...")
        BOT = MarkovChain(TARGET_FILE)
        BOT.generateDatabase(CORPUS)
        print("Dumping database to {}".format(TARGET_FILE))
        BOT.dumpdb()

        tf = TARGET_FILE.split('/')[-1]
        await ctx.channel.send(f'Generated {tf}')


    @commands.command(pass_context=True)
    async def twit(self, ctx, tag, max=5000):
        await ctx.channel.send('Scraping...')
        CORPUS = []

        if '#' in tag:
            for tweet in tweepy.Cursor(self.twe.search, q=tag, tweet_mode='extended').items(max):
                await asyncio.sleep(.01)
                if ('RT' not in tweet.full_text[:2]):
                    twet = tweet.full_text.split('http')[0]
                    if len(twet) > 25:
                        CORPUS.append(twet)
        elif '@' in tag:
            for tweet in tweepy.Cursor(self.twe.user_timeline, id=tag, tweet_mode='extended').items(max):
                await asyncio.sleep(.01)
                if ('RT' not in tweet.full_text[:2]):
                    twet = tweet.full_text.split('http')[0]
                    if len(twet) > 25:
                        if('https' in twet):
                            print(twet)
                        CORPUS.append(twet)

        try:
            os.remove(f'/home/pi/Botty/markov/{tag[1:]}.markov')
        except OSError:
            pass
        mark = MarkovChain(f'/home/pi/Botty/markov/{tag[1:]}.markov')
        mark.generateDatabase('\n'.join(CORPUS))
        mark.dumpdb()
        await ctx.channel.send(f'{tag[1:]}.markov')

    @commands.command(pass_context=True)
    async def twitttttt(self, ctx, handle, count=2000):
        handle = handle.replace('@', '')
        CORPUS = []
        tweets = await self.get_tweets(handle, count)
        for tweet in tweets:
            for twee in tweet:  
                print(twee)
                break
                CORPUS.append(twee.text)
            await asyncio.sleep(.01)


        mark = MarkovChain(f'/home/pi/Botty/markov/{handle}.markov')
        mark.generateDatabase('\n'.join(CORPUS))
        mark.dumpdb()
        await ctx.channel.send(f'{handle}.markov')


    async def get_tweets(self, screen_name, count):
        out = []
        timeline = self.twi.GetUserTimeline(screen_name=screen_name, count=min(count, 200))
        earliest_tweet = min(timeline, key=lambda x: x.id).id
        out.append(timeline)
        print("getting tweets before:", earliest_tweet)

        for i in range(int(count / 200)):
            await asyncio.sleep(.1)
            tweets = self.twi.GetUserTimeline(screen_name=screen_name, max_id=earliest_tweet, count=200)
            new_earliest = min(tweets, key=lambda x: x.id).id

            if not tweets or new_earliest == earliest_tweet:
                break
            else:
                earliest_tweet = new_earliest
                print("getting tweets before:", earliest_tweet)
                out.append(tweets)

        return out

    @commands.command(pass_context=True)
    async def history(self, ctx, number=2000):
        await ctx.channel.send('Scraping...')
        CORPUS = []
        async for message in ctx.channel.history(limit=int(number)):
            if len(message.content) < 1:
                continue
            if "!" in message.content[0]:
                continue
            if "$" in message.content[0]:
                continue
            if "[" in message.content[0]:
                continue
            if "." in message.content[0]:
                continue
            if "@" in message.content[0]:
                continue
            if "<" in message.content[0]:
                continue
            if "uwu" in message.content[:3]:
                continue
            if "pls" in message.content[:3]:
                continue
            CORPUS.append(message.content)

        try:
            os.remove(f'/home/pi/Botty/markov/{ctx.channel.name}.markov')
        except OSError:
            pass
        mark = MarkovChain(f'/home/pi/Botty/markov/{ctx.channel.name}.markov')
        mark.generateDatabase('\n'.join(CORPUS))
        mark.dumpdb()
        await ctx.channel.send(f'{ctx.channel.name}.markov')

    async def gen(self, TARGET_URL, start=1, end=10, tag=None, notags=False, nohash=False, prune=False, debug=False):
        CORPUS = ""

        for page_number in range(int(start), int(end) + 1):
            await asyncio.sleep(.1)
            print("Scraping page {}".format(page_number))
            print(TARGET_URL + str(page_number))
            soup = BeautifulSoup(requests.get(TARGET_URL + str(page_number)).text, 'lxml')

            # Search <p> tags for post content
            for para in soup.find_all('p'):
                t = para.get_text()
                if t is None:
                    continue
                if "Originally posted by" in t:
                    continue
                if "replied to your post" in t:
                    continue
                CORPUS += t + "\n"

            if notags:
                continue

            # Start the tags segment
            CORPUS += "# "
            # Search <a> tags for post tags
            for tag in soup.find_all('a'):
                h = tag.get('href')
                if h is None:
                    continue

                # Only extract tagged URLs
                if "/tagged" not in h:
                    continue

                # If there's no text, skip
                try:
                    t = tag.get_text()
                except Exception:
                    continue
                if t is None:
                    continue

                # Very commonly used tags
                if "//" in t:
                    continue
                if "cw: " in t:
                    continue

                # Prune short tags
                if prune and len(t) <= 3:
                    continue

                # Tags which are just numbers should not be in the corpus
                try:
                    int(t.strip())
                    continue
                except ValueError:
                    pass

                if nohash:
                    CORPUS += t + " "
                else:
                    CORPUS += '#' + t + " "
            CORPUS += "\n"
        if debug:
            print(CORPUS)

        return CORPUS
