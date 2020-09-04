import discord
from discord.ext.commands import Bot
from discord.ext import commands

import random
import asyncio
import random
class Others(commands.Cog):
    helpstring = []
    helpEmoji = '🇴'
    pinging = []

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!tts ; Returns a random game for TableTop Sim')

    @commands.command(pass_context=True)
    async def tts(self, ctx):
        games = ["Scythe", "House on the Hill", "Risk", "Dead of Winter", "Axis and Allies", "Isaac", "Heroscape", "Hitler"]
        await ctx.channel.send(random.choice(games))

    @commands.command(pass_context=True)
    async def bug(self, ctx):
        await ctx.channel.send('$bug')

    @commands.command(pass_context=True)
    async def itsjohnny(self,ctx):
        for i in range(random.randint(1, 10)):
            await ctx.channel.send('j.speak')
            await asyncio.sleep(random.randint(5,10) * 60)

    @commands.command(pass_context=True)
    async def pingme(self, ctx):
        if ctx.message.author.id not in self.pinging:
            self.pinging.append(ctx.message.author.id)
        else:
            self.pinging.remove(ctx.message.author.id)

        while ctx.message.author.id in self.pinging:
            await asyncio.sleep(10)
            usr = self.bot.get_user(ctx.message.author.id)
            await usr.send('ping')