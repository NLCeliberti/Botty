import discord
from discord.ext.commands import Bot
from discord.ext import commands

import random
import shutil
from insults import insult

class Wiki(commands.Cog):
    helpstring = []
    helpEmoji = '❓'

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!tarkov &search; search the wiki')
        self.helpstring.append('!!bullet ; links bullet spreadsheet')
        self.helpstring.append('!!gun ; links gun spreadsheet')
        self.helpstring.append('!!quest ; links quest items')
        self.helpstring.append('!!hideout ; links hideout items')
        self.helpstring.append('!![eft map] ; links [map]')
        self.helpstring.append('!!flow ; links flow calibration guide')
        self.helpstring.append('!!guide ; links common 3d printer issues website')
        self.helpstring.append('!!otherGuide ; links other common 3d printer issues website')
        self.helpstring.append('!!benchy ; links printer calibration guide')
        self.helpstring.append('!!tempTower ; links temp tower and breakpoints')

################################################################################
#								  EFT        								   #
################################################################################

    @commands.command(pass_context=True)
    async def tarkov(self, ctx, *args):
        await ctx.channel.send(f'https://escapefromtarkov.gamepedia.com/index.php?search={"%20".join(args)}')

    @commands.command(pass_context=True)
    async def gun(self, ctx):
        await ctx.channel.send('https://docs.google.com/spreadsheets/d/1yHyVEVB5oN0qL_pR1qTNP1_ICmzJ3SCFJQNb6XDM_DQ/edit#gid=0')

    @commands.command(pass_context=True)
    async def bullet(self, ctx):
        await ctx.channel.send('https://docs.google.com/spreadsheets/d/1VuxGkweKB118mF1kcBmVPe-Bj_gSKGOCWyoytM4miDU/edit#gid=64053005')

    @commands.command(pass_context=True)
    async def quest(self, ctx):
        await ctx.channel.send('https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/1/19/QuestItemRequirements.png')

    @commands.command(pass_context=True)
    async def hideout(self, ctx):
        await ctx.channel.send('https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/3/39/Hideout-Requirements-Items-to-Keep.jpg')

    @commands.command(pass_context=True)
    async def reserve(self, ctx):
        await ctx.channel.send('https://i.imgur.com/QTPV75c.png')

    @commands.command(pass_context=True)
    async def customs(self, ctx):
        await ctx.channel.send('https://i.imgur.com/27b2Ne5.png')

    @commands.command(pass_context=True)
    async def factory(self, ctx):
        await ctx.channel.send('https://i.imgur.com/Le3PuE1.jpg')

    @commands.command(pass_context=True)
    async def woods(self, ctx):
        await ctx.channel.send('https://i.imgur.com/fRw1XrG.png')

    @commands.command(pass_context=True)
    async def shoreline(self, ctx):
        await ctx.channel.send('https://i.imgur.com/cdyZD7l.jpg')

    @commands.command(pass_context=True)
    async def interchange(self, ctx):
        await ctx.channel.send('https://i.imgur.com/hJsAYnm.jpg')

    @commands.command(pass_context=True)
    async def labs(self, ctx):
        await ctx.channel.send('https://i.imgur.com/GDUfOwm.png')


################################################################################
#								  Print        								   #
################################################################################

    @commands.command(pass_context=True)
    async def flow(self, ctx):
        await ctx.channel.send('https://mattshub.com/blog/2017/04/19/extruder-calibration')

    @commands.command(pass_context=True)
    async def guide(self, ctx):
        await ctx.channel.send('https://www.simplify3d.com/support/print-quality-troubleshooting/')

    @commands.command(pass_context=True)
    async def otherGuide(self, ctx):
        await ctx.channel.send('https://rigid.ink/pages/ultimate-troubleshooting-guide#issue-weak-or-under-extruded-infill-21')

    @commands.command(pass_context=True)
    async def benchy(self, ctx):
        await ctx.channel.send('https://cdn.discordapp.com/attachments/367376649857269760/715915768512118834/hoa3qf6ub5gz.png')

    @commands.command(pass_context=True)
    async def tempTower(self, ctx):
        msg = []
        msg.append('Use .2 Layer height and 95% infill')
        msg.append('https://www.thingiverse.com/thing:2493504')
        for i in range(8):
            msg.append(f'{42 + i*34} : {205 - 5*i}')
        await ctx.channel.send('\n'.join(msg))
