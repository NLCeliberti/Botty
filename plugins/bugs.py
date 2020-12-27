import discord
from discord.ext.commands import Bot
from discord.ext import commands

import pickle
import zlib
import asyncio
import redis

queue = redis.StrictRedis(host='localhost', port=6379, db=0)
pubsub = queue.pubsub()
pubsub.subscribe('marketReturns')

def send_zipped_pickle(obj):
    p = pickle.dumps(obj)
    z = zlib.compress(p)
    return queue.publish('marketCommands', z)

def recv_zipped_pickle():
    z = pubsub.get_message()
    if z is not None:
        if isinstance(z['data'], bytes):
            p = zlib.decompress(z['data'])
            return pickle.loads(p)

class bugs(commands.Cog):
    helpstring = []
    helpEmoji = '🐛'

    TIMEOUT = 30 # seconds
    TREND_UPDATES = 250
    commandID = 0
    notMyCommand = {}
    
    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!stonks ; stonks')
        self.helpstring.append('!!trends ; gives insight into the market')
        self.helpstring.append('!!showMarket ; shows pretty graph')
        self.helpstring.append('!!openAccount ; become an investor') 
        self.helpstring.append('!!showInvestors ; shows everyones money')
        self.helpstring.append('!!lossPorn ; shows your history') 
        self.helpstring.append('!!showHoldings ; shows your owned stocks') 
        self.helpstring.append('!!buy &stock &amount ; Buy some stocks') 
        self.helpstring.append('!!sell &stock &amount ; Sell some stocks, \'all\' is a valid number') 
        self.helpstring.append('!!limitBuy &stock &amount &price ; Only buy the stocks if the cost drops to price') 
        self.helpstring.append('!!limitSell &stock &amount &price ; Only sell the stocks if the cost rises to price')
        self.helpstring.append('!!showLimits ; Lists all your active limit buys and sells')
        self.helpstring.append('!!cancelLimit ; Cancel a limit order, use the index from !!showLimits') 

    async def waitForRtn(self, id):
        for i in range(0, self.TIMEOUT):
            msg = recv_zipped_pickle()
            if msg:
                if msg['commandID'] == id:
                    return msg
                else:
                    self.notMyCommand[msg['commandID']] = msg
            if id in self.notMyCommand:
                msg = self.notMyCommand[id]
                del self.notMyCommand[id]
                return msg
            await asyncio.sleep(1)
        return {'error': 'Socket timed out waiting for response. Yell at nik'}

    async def sendMsg(self, msg):
        msg['commandID'] = self.commandID
        self.commandID += 1
        send_zipped_pickle(msg)
        return await self.waitForRtn(msg['commandID'])

    @commands.command(pass_context=True)
    async def trumps(self, ctx):
        await ctx.channel.send('Season 1: Sibs - Best Businessman in the buglands.')

    @commands.command(pass_context=True)
    async def configMarket(self, ctx, key, value):
        if ctx.author.id != 175732928586842113:
            await ctx.channel.send('You have no power here')
            return
        if key in self.config.keys:
            self.config[key] = value

    @commands.command(pass_context=True)
    async def trends(self, ctx):
        rtn = await self.sendMsg({'command': 'trends'})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
            return
        msg = await ctx.channel.send(rtn['msg'])
        for i in range(0, self.TREND_UPDATES):
            await asyncio.sleep(rtn['timeUntilNextUpdate'])
            rtn = await self.sendMsg({'command': 'trends'})
            if('error' in rtn):
                await ctx.channel.send(rtn['error'])
                return
            else:
                await msg.edit(content=rtn['msg'])

    @commands.command(pass_context=True)
    async def showMarket(self, ctx, stock='all', time=0):
        rtn = await self.sendMsg({'command': 'showMarket', 'stocks':stock, 'time':time})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'], file=discord.File(rtn['graph']))

    @commands.command(pass_context=True)
    async def lossPorn(self, ctx, time=0):
        rtn = await self.sendMsg({'command': 'lossPorn', 'id':ctx.author.id, 'time':time})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'], file=discord.File(rtn['graph']))

    @commands.command(pass_context=True)
    async def stonks(self, ctx):
        await ctx.channel.send(file=discord.File('/home/pi/workspace/Botty/downloads/inseks.png'))

    @commands.command(pass_context=True)
    async def showInvestors(self, ctx):
        rtn = await self.sendMsg({'command': 'showInvestors'})
        await ctx.channel.send(rtn['msg'])
    
    @commands.command(pass_context=True)
    async def showHoldings(self, ctx):
        rtn = await self.sendMsg({'command': 'showHoldings', 'id':ctx.author.id})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.author.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def openAccount(self, ctx):
        rtn = await self.sendMsg({'command': 'openAccount', 'name':ctx.author.name, 'id':ctx.author.id})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def buy(self, ctx, stock, amount):
        rtn = await self.sendMsg({'command': 'buy', 'id':ctx.author.id, 'stock':stock.upper(), 'amount':amount})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def sell(self, ctx, stock, amount=None):
        if amount is None and stock.lower() != 'all':
            await ctx.channel.send('Wtf you tryna do')
            return
        rtn = await self.sendMsg({'command': 'sell', 'id':ctx.author.id, 'stock':stock.upper(), 'amount':amount})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def limitBuy(self, ctx, stock, amount:int, limit:float):
        rtn = await self.sendMsg({'command': 'limitBuy', 'id':ctx.author.id, 'stock':stock.upper(), 'amount':amount, 'limit':limit})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def limitSell(self, ctx, stock, amount, limit:float):
        rtn = await self.sendMsg({'command': 'limitSell', 'id':ctx.author.id, 'stock':stock.upper(), 'amount':amount, 'limit':limit})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def showLimits(self, ctx):
        rtn = await self.sendMsg({'command': 'showLimits', 'id':ctx.author.id})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def cancelLimit(self, ctx, index:int):
        rtn = await self.sendMsg({'command': 'cancelLimits', 'id':ctx.author.id, 'index':index})
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(f"Removed limit {rtn['type']} for {rtn['amount']} shares of {rtn['stock']}")


