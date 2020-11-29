import discord
from discord.ext.commands import Bot
from discord.ext import commands

import random

### Change class name to anything you want
class crepe(commands.Cog):
    helpstring = []
    helpEmoji = '👁' #### Change the emoji to any you want
    #### Class variables you want

    def __init__(self, bot): 
        self.bot = bot
        self.helpstring.append('!!stinky *name')
        
    @commands.command(pass_context=True)
    async def stinky(self, ctx, name=''): #### Every command needs (self, ctx)
        KAMA = 209120745610149890
        SIBS = 194250346883842048
        DUMDUM = 188416623864971264
        NIK = 175732928586842113
                
        PassiveStink = ""
        if name.lower() == "sibs" or str(SIBS) in name:
            PassiveStink = "you're very stinky"
            name = ctx.message.guild.get_member(SIBS).mention
        elif name.lower() == "kama" or str(KAMA) in name:
            PassiveStink = "you're not stinky"
            name = ctx.message.guild.get_member(KAMA).mention
        elif name.lower() == 'bot' or str(NIK) in name:
            PassiveStink = "you're super stinky"
            name = ctx.message.guild.get_member(NIK).mention
        elif name.upper() == "CIANAN" or str(DUMDUM) in name:
            PassiveStink = "you might be stinky"
            name = ctx.message.guild.get_member(DUMDUM).mention
        else:
            PassiveStink = "you're a little stinky"
            
        if name == '':
            name = ctx.message.author.mention
            
        await ctx.channel.send (f"{name} {PassiveStink}")

    @commands.command(pass_context=True)
    async def diceRoll (self, ctx): ##No arguments needed, as there is no outside input required.
        rollOne = random.randrange(1, 20) ##Roll the first number.
        rollTwo = random.randrange(1, 20) ##Roll the second number.

        rollOutcome = ""
        if rollOne > rollTwo:
            rollOutcome = ("YOU ARE NOT THE LOSER.")

        elif rollTwo > rollOne:
            rollOutcome = ("YOU ARE THE LOSER.")

        else:
            rollOutcome = ("TODAY, YOU HAVE BOTH LOST.")
        await ctx.channel.send (f'YOU ROLLED {rollOne}.\nBOTTY ROLLED {rollTwo}.\n{rollOutcome}')

    @commands.command(pass_context=True)
    async def challenge(self, ctx, user: discord.Member = None):
        ctx.channel.send(f'YOU HAVE BEEN CHALLENGED, {user.mention}. WILL YOU ACCEPT?')

        self.timeout()
