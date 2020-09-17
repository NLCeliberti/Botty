import discord
from discord.ext.commands import Bot
from discord.ext import commands

import asyncio
import pandas
import random
import matplotlib
import os

class bugs(commands.Cog):
    helpstring = []
    helpEmoji = '🐛'
    running = False
    stockMarket = None
    
    def __init__(self, bot):
        self.bot = bot
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

        self.stockMarket = stock_engine()

    @commands.command(pass_context=True)
    async def s(self, ctx):
        if ctx.author.id != 175732928586842113:
            await ctx.channel.send('You have no power here')
            return
        await self.stockMarket.save()
        await ctx.channel.send('Saved')
        await self.stockMarket.startMarket()    

    @commands.command(pass_context=True)
    async def configMarket(self, ctx, key, value):
        if ctx.author.id != 175732928586842113:
            await ctx.channel.send('You have no power here')
            return
        if key in self.config.keys:
            self.config[key] = value

    @commands.command(pass_context=True)
    async def startMarket(self, ctx):
        if ctx.author.id != 175732928586842113:
            await ctx.channel.send('You have no power here')
            return
        await self.stockMarket.startMarket()

    @commands.command(pass_context=True)
    async def stopMarket(self, ctx):
        if ctx.author.id != 175732928586842113:
            await ctx.channel.send('You have no power here')
            return
        await self.stockMarket.stopMarket()

    @commands.command(pass_context=True)
    async def trends(self, ctx):
        rtn = await self.stockMarket.showTrends()
        await ctx.channel.send(rtn)

    @commands.command(pass_context=True)
    async def showMarket(self, ctx, stock='all', time=0):
        rtn = await self.stockMarket.showMarket(stock, time)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'], file=discord.File(rtn['graph']))

    @commands.command(pass_context=True)
    async def lossPorn(self, ctx, time=0):
        rtn = await self.stockMarket.lossPorn(ctx.author.id, time)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'], file=discord.File(rtn['graph']))

    @commands.command(pass_context=True)
    async def stonks(self, ctx):
        await ctx.channel.send(file=discord.File('/home/pi/Botty/downloads/inseks.png'))

    @commands.command(pass_context=True)
    async def showInvestors(self, ctx):
        rtn = await self.stockMarket.showInvestors()
        await ctx.channel.send(rtn)
    
    @commands.command(pass_context=True)
    async def showHoldings(self, ctx):
        rtn = await self.stockMarket.showHoldings(ctx.author.id)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.author.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def openAccount(self, ctx):
        rtn = await self.stockMarket.openAccount(ctx.author.name, ctx.author.id)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send('Welcome Investor!')

    @commands.command(pass_context=True)
    async def buy(self, ctx, stock, amount:int):
        rtn = await self.stockMarket.buy(ctx.author.id, stock.upper(), amount)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def sell(self, ctx, stock, amount):
        rtn = await self.stockMarket.sell(ctx.author.id, stock.upper(), amount)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def limitBuy(self, ctx, stock, amount:int, limit:float):
        rtn = await self.stockMarket.limitBuy(ctx.author.id, stock.upper(), amount, limit)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def limitSell(self, ctx, stock, amount, limit:float):
        rtn = await self.stockMarket.limitSell(ctx.author.id, stock.upper(), amount, limit)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def showLimits(self, ctx):
        rtn = await self.stockMarket.showLimits(ctx.author.id)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(rtn['msg'])

    @commands.command(pass_context=True)
    async def cancelLimit(self, ctx, index:int):
        rtn = await self.stockMarket.cancelLimit(ctx.author.id, index)
        if 'error' in rtn:
            await ctx.channel.send(rtn['error'])
        else:
            await ctx.channel.send(f"Removed limit {rtn['type']} for {rtn['amount']} shares of {rtn['stock']}")


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
    stocks = {}
    investors = {}
    tick = 0
    
    def __init__(self):
        self.config = {'ticks': 2}
        self.marketGrowthFactor = .1

        if PERSISTENT:
            if os.path.exists(self.STOCK_SAVE_FP):
                with open(self.STOCK_SAVE_FP, 'r') as f:
                    data = f.readline().strip().split('|')
                    self.tick = int(data[0])
                    self.marketGrowthFactor = float(data[1])
                    for line in f.readlines():
                        data = line.strip().split('|')
                        if data[0] == 'stock':
                            self.stocks[data[2]] = stock(data[1], data[2], float(data[3]), int(data[4]), data[5])
                        elif data[0] == 'investor':
                            self.investors[int(data[2])] = investor(data[1], int(data[2]), float(data[3]), data[4], data[5], data[6], data[7])
            else:
                for sts, st in self.STOCKS.items():
                    self.stocks[sts] = stock(st, sts, random.randint(100,200), random.randint(RISK_LOWER, RISK_UPPER))
        else:
            for sts, st in self.STOCKS.items():
                self.stocks[sts] = stock(st, sts, random.randint(100,200), random.randint(RISK_LOWER, RISK_UPPER))

    async def startMarket(self):
        if not self.running:
            self.running = True
            await self.updateMarket()

    async def stopMarket(self):
        if self.running:
            self.running = False

    async def updateMarket(self):
        while self.running:
            if self.tick % self.config['ticks'] * 60 * 60 == 0:  # Save every hour... probably
                await self.save()
                self.running = True

            await asyncio.sleep(60 / int(self.config['ticks']))
            if random.randint(0,100) < self.MARKET_VOLATILENESS:
                rfactor = 1 if (random.randint(0,100) > 50 * (1 + 16*(self.marketGrowthFactor * abs(self.marketGrowthFactor)))) else -1 
                self.marketGrowthFactor += rfactor * random.randint(1,3) * .01
                #print(self.marketGrowthFactor)
            self.tick += 1
            for st in self.stocks.values():
                st.updatePrice(self.tick, self.marketGrowthFactor)

            for inv in self.investors.values():
                for lim in inv.limits:
                    if lim['type'] == 'buy':
                        if self.stocks[lim['stock']].price <= lim['limit']:
                            inv.buy(lim['stock'], lim['amount'], lim['limit'])
                            inv.limits.remove(lim)
                    else:
                        if self.stocks[lim['stock']].price >= lim['limit']:
                            inv.buy(lim['stock'], lim['amount'], lim['limit'])
                            inv.limits.remove(lim)
                stocksPrice = 0
                for stk in inv.portfolio:
                    stocksPrice += self.stocks[stk].price * inv.portfolio[stk]
                inv.update(self.tick, stocksPrice)
            

    async def showTrends(self):
        msg = []
        msg.append('```ini\n')
        msg.append(f'MGF: {self.marketGrowthFactor:.2f}')
        for st in self.stocks.values():
            msg.append(f'[{st.short_name:3}] ${st.price:4.2f} {st.riskFactor}')
        msg.append('\n```')

        return '\n'.join(msg)

    async def showInvestors(self):
        msg = []
        msg.append('```ini\n')

        for inv in self.investors.values():
            stocks = 0
            for stk in inv.portfolio:
                stocks += self.stocks[stk].price * inv.portfolio[stk]
            msg.append(f'[{inv.name:^25}] Total ${inv.money + stocks:4.2f}\tCash ${inv.money:4.2f}\tStocks ${stocks:4.2f}')
        msg.append('\n```')

        return '\n'.join(msg)

    async def showMarket(self, stock='all', time=0):
        if time == 0:
            time = self.tick
        showList = []
        if stock.lower() == 'all':
            showList = self.STOCKS.keys()
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

        for name in showList:
            msg.append(f'{self.stocks[name].name:25}  [${self.stocks[name].price:.2f}]')
            data[name] = list(self.stocks[name].priceHistory.values())
        df = pandas.DataFrame(data, index=list(range(0, self.tick + 1)))
        df = df.loc[df.index > self.tick + 1 - time]
        graph = df.plot.line()
        fig = graph.get_figure()
        fig.savefig(marketGraph)
        matplotlib.pyplot.close(fig)
        msg.append('\n```')

        return {'msg':'\n'.join(msg), 'graph':marketGraph}


    async def lossPorn(self, uid, time=0):
        if time == 0:
            time = self.tick

        if uid in self.investors:
            lossGraph = '/home/pi/Botty/downloads/lossporn.png'
            data = {}

            data[self.investors[uid].name] = self.investors[uid].history

            df = pandas.DataFrame(data, index=list(range(0, self.tick + 1)))
            df = df.loc[df.index > self.tick + 1 - time]
            graph = df.plot.line()
            fig = graph.get_figure()
            fig.savefig(lossGraph)
            matplotlib.pyplot.close(fig)

            return {'msg': '', 'graph':lossGraph}
        else:
            return {'error': 'Make an account ya goober'}

    async def showHoldings(self, uid):
        if uid in self.investors:
            msg = []
            msg.append('```ini\n')
            for stk in self.investors[uid].portfolio:
                msg.append(f'[{self.investors[uid].portfolio[stk]}] shares of [{stk}]')
            msg.append('\n```')
            return {'msg': '\n'.join(msg)}
        else:
            return {'error': 'Make an account ya goober'}

    async def save(self):
        self.running = False 
        await asyncio.sleep(60 / int(self.config['ticks']))  # Ensure that the last tick finishes before we save off data

        with open(self.STOCK_SAVE_FP, 'w+') as f:
            f.write(f'{self.tick}|{self.marketGrowthFactor}\n')
            for stk in self.stocks.values():
                f.write(f'stock|{stk.name}|{stk.short_name}|{stk.price}|{stk.riskFactor}|{stk.priceHistory}\n')
            for inv in self.investors.values():
                f.write(f'investor|{inv.name}|{inv.uid}|{inv.money}|{inv.portfolio}|{inv.transactions}|{inv.history}|{inv.limits}\n')

    async def openAccount(self, name, uid):
        if int(uid) in self.investors.keys():
            return {'error': 'Account already Exists'}
        self.investors[int(uid)] = (investor(name, uid))
        return {}

    async def buy(self, uid, stk, amount:int):
        if uid not in self.investors.keys():
            return {'error': 'You need to open an account dumdum'}
        if stk in self.stocks.keys():
            return self.investors[uid].buy(stk, amount, self.stocks[stk].price)
        else:
            return {'error': 'Try a real stock'}

    async def sell(self, uid, stk, amount):
        if uid not in self.investors.keys():
            return {'error': 'You need to open an account dumdum'}
        if stk in self.stocks.keys():
            return self.investors[uid].sell(stk, amount, self.stocks[stk].price)
        else:
            return {'error': 'Try a real stock'}

    async def limitBuy(self, uid, stk, amount:int, limit):
        if uid not in self.investors.keys():
            return {'error': 'You need to open an account dumdum'}
        if stk in self.stocks.keys():
            return self.investors[uid].limitBuy(stk, amount, limit)

    async def limitSell(self, uid, stk, amount, limit):
        if uid not in self.investors.keys():
            return {'error': 'You need to open an account dumdum'}
        if stk in self.stocks.keys():
            return self.investors[uid].limitSell(stk, amount, limit)

    async def showLimits(self, uid):
        if uid not in self.investors.keys():
            return {'error': 'You need to open an account dumdum'}

        msg = []
        msg.append('```ini\n')

        if len(self.investors[uid].limits) == 0:
            return {'msg': 'You have no limits'}

        for lim, i in zip(self.investors[uid].limits, range(0, len(self.investors[uid].limits))):
            msg.append(f"{i}: [{lim['type']} {lim['amount']} {lim['stock']} at {lim['limit']}]")
        
        msg.append('\n```')

        return {'msg': '\n'.join(msg)}

    async def cancelLimit(self, uid, index):
        if index + 1 <= len(self.investors[uid].limits):
            return self.investors[uid].limits.pop(index)
        else:
            return {'error': 'Not a valid index'}


class stock():
    riskFactor = None  # 1-100 1 being extremely safe, 100 being extrememly dangerous
    price = None
    priceHistory = None  # {tick: price}
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
    transactions = None
    history = None
    limits = []

    def __init__(self, name, uid, money=1500.0, portfolio=None, transactions=None, history=None, limits=None):
        self.name = name
        self.uid = uid
        self.money = money
        if portfolio is None:
            self.portfolio = {} # {STK: amount}
        else:
            exec(f'self.portfolio = {portfolio}')

        if transactions is None:
            self.transactions = []
        else:
            exec(f'self.transactions = {transactions}')

        if history is None:
            self.history = {}
        else:
            exec(f'self.history = {history}')

        if limits is None:
            self.limits = []
        else:
            exec(f'self.limits = {limits}')

    def update(self, tick, stockPrice):
        if tick % 1000 == 0:
            self.money += 100.0
        self.history[tick] = stockPrice + self.money

    def buy(self, stock, amount, priceeach):
        total_price = priceeach * amount

        if amount <= 0:
            return {'error': 'Try buying a real amount of stocks plz'}

        if self.money >= total_price:
            self.money -= total_price
            if stock in self.portfolio:
                self.portfolio[stock] = self.portfolio[stock] + amount
            else:
                self.portfolio[stock] = {}
                self.portfolio[stock] = amount
            self.transactions.append(f'Bought {amount} shares of {stock} for {priceeach} each.')
            return {'msg': random.choice(['Nice Purchase', 'Wrong Move, dumdum', '... Are you sure?', 'I have a good feeling about this.', 'lmao', 'To the mooooooooooooon'])}
        else:
            return {'error': 'Not enough money loserman'}

    def sell(self, stock, amount, priceeach):
        if stock in self.portfolio:
            if amount == 'all':
                amount = self.portfolio[stock]
            else:
                amount = int(amount)
            if self.portfolio[stock] >= amount:
                total_price = priceeach * amount
                self.portfolio[stock] -= amount

                self.money += total_price
                self.transactions.append(f'Sold {amount} shares of {stock} for {priceeach} each.')
                if self.portfolio[stock] == 0:
                    del self.portfolio[stock]
                return {'msg': random.choice(['Nice Sell', 'Wrong Move, dumdum', '... Are you sure?', 'I have a good feeling about this.', 'lmao', 'Wrong moon?'])}
            else:
                return {'error': 'You do not have that many shares stoopid'}
        else:
            return {'error': 'You don\'t even have that stock '}

    def limitBuy(self, stock, amount, limit):
        if self.money >= amount * limit:
            self.limits.append({'stock': stock, 'amount':amount, 'limit':limit, 'type': 'buy'})
            self.money -= amount * limit
            return {'msg': 'Limit set!'}
        else:
            return {'error': 'Not enough money loserman'}

    def limitSell(self, stock, amount, limit):
        if stock in self.portfolio:
            if amount == 'all':
                amount = self.portfolio[stock]

            if self.portfolio[stock] >= amount:
                self.limits.append({'stock': stock, 'amount':amount, 'limit':limit, 'type': 'sell'})
                return {'msg': 'Limit set!'}
            else:
                return {'error': 'You do not have that many shares stoopid'}
        else:
            return {'error': 'You don\'t even have that stock '}
