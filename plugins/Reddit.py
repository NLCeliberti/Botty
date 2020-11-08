import discord
from discord.ext.commands import Bot
from discord.ext import commands

import praw
import random



class Reddit(commands.Cog):
    helpstring = []
    helpEmoji = '📕'
    reddit = None

    client = None
    secret = None
    user_agent = None

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!hot &subreddit ; Post from top 10 current posts in subreddit')
        self.helpstring.append('!!random ; random post from random subreddit')
        self.helpstring.append('!!cat ; cat')
        self.helpstring.append('!!pic ; pic')

        with open('/home/pi/Botty/deps/reddit.txt', 'r') as f:
            _ = f.read().split('\n')
            self.client = _[0].strip()
            self.secret = _[1].strip()
            self.user_agent = _[2].strip()

        self.reddit = praw.Reddit(client_id=self.client,
                             client_secret=self.secret,
                             user_agent=self.user_agent)

    @commands.command(pass_context=True)
    async def hot(self, ctx, subreddit):
        for submission in self.reddit.subreddit(subreddit).hot(limit=1):
            embed = discord.Embed(title=submission.title, description=submission.selftext, color=0x000aff)
            embed.set_image(url=submission.url)
            await ctx.channel.send(embed=embed)

    @commands.command(pass_context=True)
    async def random(self, ctx):
        for submission in self.reddit.subreddit('random').hot(limit=10):
            if(submission.stickied):
                continue
            if(submission.over_18 and not ctx.channel.is_nsfw()):
                await ctx.channel.send('Picked a NSFW subreddit')
            await ctx.channel.send(f'https://www.reddit.com{submission.permalink}')
            return

    @commands.command(pass_context=True)
    async def cat(self, ctx):
        subs = ['meow_irl', 'cats', 'catpics', 'illegallysmolcats', 'kitten', 'kittens', 'kitties', 'lookatmycat', 'cat', 'kitty', 'catpictures', 'catloaf', 'floof', 'blep', 'catsstandingup', 'catbellies', 'tightpussy', 'murdermittens', 'supermodelcats', 'holdmycatnip']
        skip = random.randint(0,9)
        count = 0
        for submission in self.reddit.subreddit(random.choice(subs)).hot(limit=10):
            if(count < skip):
                count += 1
                continue
            if(submission.stickied):
                continue
            check = self.checkURL(submission)
            if check[0]:
                await ctx.channel.send(embed=check[1])
            else:
                await ctx.channel.send(check[1])
            return

    @commands.command(pass_context=True)
    async def pic(self, ctx, subreddit=None):
        subs = []
        filepath = '/home/pi/Botty/deps/pics.txt'
        if(subreddit is not None):
            with open(filepath, 'r') as f:
                new = True
                for l in f.readlines():
                    subs.append(l.replace('\n',''))
                    if subreddit in l:
                        new = False
            if(new):
                with open(filepath, 'a') as f:
                    f.write(subreddit + '\n')
                    subs.append(subreddit)
        else:
            with open(filepath, 'r') as f:
                for l in f.readlines():
                    subs.append(l.replace('\n',''))
        skip = random.randint(0,9)
        count = 0
        for submission in self.reddit.subreddit(random.choice(subs)).hot(limit=10):
            if(count < skip):
                count += 1
                continue
            check = self.checkURL(submission)
            if check[0]:
                print(check)    
                await ctx.channel.send(embed=check[1])
            else:
                await ctx.channel.send(check[1])
            return

    def checkURL(self, submission):
        print(submission.url)
        if 'v.redd' in submission.url:
            return [False, 'Get fucked by v.redd.it']
        if '.gifv' in submission.url or 'youtu' in submission.url:
            return [False, f'{submission.title}\n{submission.url}']
        if 'imgur' in submission.url and 'i.imgur' not in submission.url:
            embed = discord.Embed(title=submission.title, description=f'[/r/{submission.subreddit.display_name}](https://www.reddit.com/r/{submission.subreddit.display_name})', color=0x000aff)
            url = submission.url + '.jpg'
            url = url.replace('imgur', 'i.imgur')
            embed.set_image(url=url)
            return [True, embed]

        embed = discord.Embed(title=submission.title, description=f'[/r/{submission.subreddit.display_name}](https://www.reddit.com/r/{submission.subreddit.display_name})', color=0x000aff)
        embed.set_image(url=submission.url)
        return [True, embed]
#    @commands.command(pass_context=True)
#    async def random(self, ctx):
#        for submission in self.reddit.subreddit('random').hot(limit=10):
#            if(submission.stickied):
#                continue
#            if(submission.over_18 and not ctx.channel.is_nsfw()):
#                continue
#            await ctx.channel.send(f'Pulled from: {submission.subreddit}')
#            embed = discord.Embed(title=submission.title, description=submission.selftext[:2047], color=0x00ff00)
#            embed.set_image(url=submission.url)
#            await ctx.channel.send(embed=embed)
#            return
