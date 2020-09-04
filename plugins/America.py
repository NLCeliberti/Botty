import discord
from discord.ext.commands import Bot
from discord.ext import commands

import picamera
import asyncio

class America(commands.Cog):
    helpstring = []
    helpEmoji = '🔫'
    ypos = 0
    ymin = 0
    ymax = 90
    xpos = 0

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!fire')
        self.helpstring.append('!!x &degrees')
        self.helpstring.append('!!y &degrees')
        self.helpstring.append('!!ammo')
        self.helpstring.append('!!lmao')

    @commands.command(pass_context=True)
    async def view(self, ctx):
        await sendPic(self, ctx)

    @commands.command(pass_context=True)
    async def fire(self, ctx):
        await ctx.channel.send('pew pew')

    @commands.command(pass_context=True)
    async def x(self, ctx, change:int):
        nik = self.bot.get_user(175732928586842113)
        await nik.send(f'{ctx.message.guild} :: {ctx.message.channel} :: {ctx.message.author} ::: {ctx.message.content}')
        self.xpos = self.xpos + change % 360
        await sendPic(self, ctx)

    @commands.command(pass_context=True)
    async def y(self, ctx, change:int):
        if (self.ymin < self.ypos + change and self.ypos + change < self.ymax):
            self.ypos = self.ypos + change
            await nik.send(f'{ctx.message.guild} :: {ctx.message.channel} :: {ctx.message.author} ::: {ctx.message.content}')
            await sendPic(self, ctx)
        else:
            await ctx.channel.send('ur illegal')


    async def sendPic(self, ctx):
        await self.pic()
        file = discord.File('/home/pi/Botty/downloads/pic.jpg', filename="pic.jpg")
        await ctx.channel.send(f'{self.ypos}', file=file)

    async def pic(self):
        nik = self.bot.get_user(175732928586842113)
        await nik.send('Camera on')
        await asyncio.sleep(2)
        camera = picamera.PiCamera()
        camera.start_preview()
        await asyncio.sleep(3)
        camera.capture('/home/pi/Botty/downloads/pic.jpg')
        camera.stop_preview()
        camera.close()
        
    @commands.command(pass_context=True)
    async def ammo(self, ctx):
        await ctx.channel.send('reloading')
    
    @commands.command(pass_context=True)
    async def lmao(self, ctx):
        await ctx.channel.send('More Bullets More Death')