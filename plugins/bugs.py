import discord
from discord.ext.commands import Bot
from discord.ext import commands

import asyncio
import pandas
import random
import matplotlib

class bugs(commands.Cog):
    helpstring = []
    helpEmoji = '🐛'
    running = False
    stockMarket = None
    
    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('')
        self.helpstring.append('') 
        self.stockMarket = stock_engine()

    @commands.command(pass_context=True)
    async def trends(self, ctx):
        out = await self.stockMarket.showTrends()
        await ctx.channel.send(out)

    @commands.command(pass_context=True)
    async def configMarket(self, ctx, key, value):
        if key in self.config.keys:
            self.config[key] = value

    @commands.command(pass_context=True)
    async def startMarket(self, ctx):
        await self.stockMarket.startMarket()

    @commands.command(pass_context=True)
    async def stopMarket(self, ctx):
        await self.stockMarket.stopMarket()

    @commands.command(pass_context=True)
    async def showMarket(self, ctx, stock='all', time=0):
        out = await self.stockMarket.showMarket(stock, time)
        if 'error' in out:
            await ctx.channel.send(out['error'])
            return
        await ctx.channel.send(out['msg'], file=discord.File(out['graph']))

    @commands.command(pass_context=True)
    async def showInvestors(self, ctx):
        out = await self.stockMarket.showInvestors()
        await ctx.channel.send(out)
    
    @commands.command(pass_context=True)
    async def s(self, ctx):
        await self.stockMarket.save()
        await ctx.channel.send('Saved')
        await self.stockMarket.startMarket()       

    @commands.command(pass_context=True)
    async def openAccount(self, ctx):
        rtn = await self.stockMarket.openAccount(ctx.author.name, ctx.author.id)
        if rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send('Welcome Investor!')

    @commands.command(pass_context=True)
    async def buy(self, ctx, stock, amount):
        pass

RISK_LOWER = 40
RISK_UPPER = 50
PERSISTENT = False

class stock_engine():
    MARKET_VOLATILENESS = 15  # 0-100 0 being C4, 100 being a politcal discussion during thanksgiving 
    STOCK_SAVE_FP = '/home/pi/Botty/deps/stockMarket.txt'
    STOCKS = {'CCS':'Cuban Crescentspot', 'RBS':'Red-Bodied Swallowtail', 'RFL':'Rat Flea', 'SYL':'Shy Yellow'}
    running = False
    marketGrowthFactor = None  # between -1 and 1
    config = None
    stocks = []
    investors = {}
    tick = 0
    
    def __init__(self):
        self.config = {'ticks': 120}
        self.marketGrowthFactor = .1

        if PERSISTENT:
            with open(self.STOCK_SAVE_FP, 'r') as f:
                data = f.readline().strip().split('|')
                self.tick = int(data[0])
                self.marketGrowthFactor = float(data[1])
                for line in f.readlines():
                    data = line.strip().split('|')
                    if data[0] == 'stock':
                        self.stocks.append(stock(data[1], data[2], float(data[3]), int(data[4]), data[5]))
                    elif data[0] == 'investor':
                        self.investors[int(data[2])] = investor(data[1], int(data[2]), data[3], int(data[4]), data[5])
        else:
            for sts, st in self.STOCKS.items():
                self.stocks.append(stock(st, sts, random.randint(20,40), random.randint(RISK_LOWER, RISK_UPPER)))

    async def startMarket(self):
        if not self.running:
            self.running = True
            await self.updateMarket()

    async def stopMarket(self):
        if self.running:
            self.running = False

    async def updateMarket(self):
        while self.running:
            await asyncio.sleep(60 / int(self.config['ticks']))
            if random.randint(0,100) < self.MARKET_VOLATILENESS:
                rfactor = 1 if (random.randint(0,100) > 50 * (1 + 16*(self.marketGrowthFactor * abs(self.marketGrowthFactor)))) else -1 
                self.marketGrowthFactor += rfactor * random.randint(1,3) * .01
                print(self.marketGrowthFactor)
            self.tick += 1
            for st in self.stocks:
                st.updatePrice(self.tick, self.marketGrowthFactor)

    async def showTrends(self):
        msg = []
        msg.append('```ini\n')
        msg.append(f'MGF: {self.marketGrowthFactor:.2f}')
        for st in self.stocks:
            msg.append(f'[{st.short_name:3}] ${st.price:4.2f} {st.riskFactor}')
        msg.append('\n```')

        return '\n'.join(msg)

    async def showInvestors(self):
        msg = []
        msg.append('```ini\n')
        for inv in list(self.investors.values()):
            msg.append(f'[{inv.name}] ${inv.money:4.2f}')
        msg.append('\n```')

        return '\n'.join(msg)

    async def showMarket(self, stock='all', time=0):
        if time == 0:
            time = self.tick
        showList = []
        if stock.lower() == 'all':
            showList = list(self.STOCKS.keys())
        elif ':' in stock:
            stks = stock.split(':')
            for stk in stks:
                if stk.upper() in self.STOCKS.keys():
                    showList.append(stk.upper())
                else:
                    return {'error':f'{stk} is not real dummyhead'}
        else:
            if stock.upper() in self.STOCKS.keys():
                    showList.append(stock.upper())
            else:
                return {'error':f'{stock} is not real dummyhead'}
            
        marketGraph = '/home/pi/Botty/downloads/market.png'
        msg = []
        msg.append('```ini\n')
        data = {}
        for st in self.stocks:
            if st.short_name not in showList:
                continue
            msg.append(f'{st.name:25}  [${st.price:.2f}]')
            data[st.short_name] = list(st.priceHistory.values())
        df = pandas.DataFrame(data, index=list(range(0, self.tick + 1)))
        df = df.loc[df.index > self.tick + 1 - time]
        graph = df.plot.line()
        fig = graph.get_figure()
        fig.savefig(marketGraph)
        matplotlib.pyplot.close(fig)
        msg.append('\n```')

        return {'msg':'\n'.join(msg), 'graph':marketGraph}

    async def save(self):
        self.running = False 
        await asyncio.sleep(60 / int(self.config['ticks']))  # Ensure that the last tick finishes before we save off data

        with open(self.STOCK_SAVE_FP, 'w+') as f:
            f.write(f'{self.tick}|{self.marketGrowthFactor}\n')
            for stk in self.stocks:
                f.write(f'stock|{stk.name}|{stk.short_name}|{stk.price}|{stk.riskFactor}|{stk.priceHistory}\n')
            for inv in list(self.investors.values()):
                f.write(f'investor|{inv.name}|{inv.money}|{inv.portfolio}|{inv.total_gains}|{inv.history}')

    async def openAccount(self, name, uid):
        if int(uid) in list(self.investors.keys()):
            return {'error': 'Account already Exists'}
        self.investors[int(uid)] = (investor(name, uid))
        return None

    async def buy(self, uid, stk, amount:int):
        bought = False
        for stock in self.stocks:
            if stk.upper() == stock.short_name:
                total_price = stock.price * amount

            

class stock():
    riskFactor = None  # 1-100 1 being extremely safe, 100 being extrememly dangerous
    price = None
    priceHistory = None  # {tick, price}
    newsHistory = None
    name = None
    short_name = None

    def __init__(self, name, short_name, price, risk, priceHistory=None):
        self.name = name
        self.short_name = short_name
        self.price = price
        self.riskFactor = risk
        if priceHistory:
            exec(f'self.priceHistory = {priceHistory}')
        else:
            self.priceHistory = {0: self.price}
        self.newsHistory = []

    def updatePrice(self, tick, mgf):
        if random.randint(0, 100) < 10:
            self.riskFactor += random.choice([1, -1])
            if self.riskFactor < RISK_LOWER:
                self.riskFactor = RISK_LOWER
            if self.riskFactor > RISK_UPPER:
                self.riskFactor = RISK_UPPER

        if random.randint(0, 100) >= self.riskFactor * (1 - mgf) * (1 + self.price / 1000):
            x = (1 + abs(mgf) * random.randint(0, 10)/100)
            #print(f'upwards: {x}')
            self.price = self.price * x
        else:
            x = (1 - abs(mgf) * random.randint(0, 10)/100)
            #print(f'downwards:  {x}')
            self.price = self.price * x

        self.priceHistory[tick] = self.price


class investor():
    name = None
    uid = None
    money = None
    portfolio = None
    total_gains = None
    history = None

    def __init__(self, name, uid, money=1500, portfolio=None, total_gains=0, history=None):
        self.name = name
        self.money = money
        if portfolio is None:
            self.portfolio = {}
        else:
            exec(f'self.portfolio = {portfolio}')
        self.total_gains = total_gains

        if history is None:
            self.history = {}
        else:
            exec(f'self.history = {history}')