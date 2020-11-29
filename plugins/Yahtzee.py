import discord
from discord.ext.commands import Bot
from discord.ext import commands

import random
import asyncio

def mentionToID(mention):
    return int(mention.split('<@!')[1].split('>')[0])

class Yahtzee(commands.Cog):
    helpstring = []
    helpEmoji = '🎲'
    ongoingGame = None
    dieToEmoji = {1:'1️⃣', 2:'2️⃣', 3:'3️⃣', 4:'4️⃣', 5:'5️⃣', 6:'6️⃣'}
    
    waysToScore = { 'ones': 'The number of 1s you rolled',
                    'twos': 'The number of 2s you rolled', 
                    'threes': 'The number of 3s you rolled', 
                    'fours': 'The number of 4s you rolled', 
                    'fives': 'The number of 5s you rolled', 
                    'sixes': 'The number of 6s you rolled',
                    'BONUS': 'Automatically given if you score above 62 for the 1-6 scores - 35 points',
                    '3x': 'The face value of the die as long as you have 3 of a kind',
                    '4x': 'The face value of the die as long as you have 4 of a kind',
                    'full': 'A full house - 25 points',
                    'small': 'A small straight (4 in a row) - 30 points',
                    'large': 'A large straight (5 in a row) - 40 points',
                    '5x': 'YAHTZEEEEEEEEEEEE - 50 points for the first one [100 for each after as well as an additional scoring option!]',
                    'chance': 'The face value of the die'
                    }

    aliases = { '1': 'ones', '1s': 'ones',
                '2': 'twos', '2s': 'twos',
                '3': 'threes', '3s': 'threes',
                '4': 'fours', '4s': 'fours',
                '5': 'fives', '5s': 'fives',
                '6': 'sixes', '6s': 'sixes',
                'yahtzee': '5x'
                }

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('Welcome to yahtzee. You can only be in 1 game at a time.')
        self.helpstring.append('!!yahtzee &@person ; Mention someone to start a game with them')
        self.helpstring.append('!!yroll (yr) *keep ; roll the die! list all the ones you want to keep e.g. !!yroll 1 1 1')
        self.helpstring.append('!!yscore (ys) &category ; scores the rolls with the given category !!ycategory to see how scoring works')

    @commands.command(pass_context=True)
    async def yahtzee(self, ctx, *players):
        if players is ():
            await ctx.channel.send(f'{ctx.author.mention} is a stupid fuck that needs to read the rules.')
        elif len(players) > 1:
            await ctx.channel.send(f'Yell at <@!175732928586842113> if you want to be able to play with more people.')
        elif self.ongoingGame:
            await ctx.channel.send(f'Bitch at <@!175732928586842113> if you want to have more than 1 game going on at a time.')
        elif '<@!365647831412899841>' in players:
            await ctx.channel.send(f'<@!365647831412899841> dominated you in that game of Yahtzee.')
        elif ctx.author.mention in players:
            await ctx.channel.send(f'{ctx.author.mention} is trying to diddle themselves!')
        else:
            players = [mentionToID(x) for x in players]
            players.append(ctx.author.id)
            gameState = {'timesRolled': 0, 'rolls':[], 'players': {}}
            for player in players:
                gameState['players'][player] = {'alreadyScored': {}}
            self.ongoingGame = Game('Yahtzee', players, gameState)
            await ctx.channel.send(f"{self.ongoingGame.game} initiated with {', '.join([f'<@!{player}>' for player in players])}\nIt is {self.ongoingGame.whoseTurn()}'s Turn\nMake a move to accept the game!")
            await asyncio.sleep(30)
            if not self.ongoingGame.accepted:
                await ctx.channel.send(f'{self.ongoingGame.whoseTurn()} is a little bitch and never accepted. *Bitch.*')
                self.ongoingGame = None

    @commands.command(pass_context=True)
    async def ycategory(self, ctx):
        out = []
        out.append('```ini\n\n')
        for cat in self.waysToScore:
            out.append(f"{'[' + cat.title() + ']':9} {self.waysToScore[cat]}")
        out.append('\n```')
        await ctx.channel.send('\n'.join(out))

    @commands.command(pass_context=True)
    async def yr(self, ctx, *keep):
        await self.yroll(ctx, keep)

    @commands.command(pass_context=True)
    async def yroll(self, ctx, *keep):
        for i in keep:
            if isinstance(i, tuple):
                keep = i
        if await self.canPlay(ctx):
            if not self.ongoingGame.accepted:
                self.ongoingGame.accept()
            if self.ongoingGame.gameState['timesRolled'] >= 3:
                await ctx.channel.send(f'{ctx.author.mention} is trying to cheat by rolling too much.')
                return
            keptDie = []
            if keep:
                for die in keep:
                    die = int(die)
                    canKeep = False
                    for roll in self.ongoingGame.gameState['rolls']:
                        if die == roll:
                            canKeep = True
                            self.ongoingGame.gameState['rolls'].remove(die)
                            keptDie.append(die)
                            break
                    if not canKeep:
                        await ctx.channel.send(f'{ctx.author.mention} you can\'t keep a {die} you dumb fucker.')
                        self.ongoingGame.gameState['rolls'].extend(keptDie)
                        return
            self.ongoingGame.gameState['rolls'] = keptDie
            for x in range(0, 5 - len(keep)):
                self.ongoingGame.gameState['rolls'].append(random.randint(1,6))
            await ctx.channel.send(f"{' '.join([self.dieToEmoji[x] for x in self.ongoingGame.gameState['rolls']])}")
            self.ongoingGame.gameState['timesRolled'] += 1
        
    @commands.command(pass_context=True)
    async def ys(self, ctx, category):
        await self.yscore(ctx, category)

    @commands.command(pass_context=True)
    async def yscore(self, ctx, category):
        if await self.canPlay(ctx):
            if category in self.aliases:
                category = self.aliases[category]
            if category in self.waysToScore:
                if category in self.ongoingGame.gameState['players'][ctx.author.id]['alreadyScored']:
                    await ctx.channel.send('You\'ve already scored that you fuck.')
                    return
                score = await self.calculateScore(category)
                
                if self.determine5x()['score'] == 50 and '5x' in self.ongoingGame.gameState['players'][ctx.author.id]['alreadyScored']:
                    self.ongoingGame.changeScore(ctx.author.id, 100)
                    await ctx.channel.send(f"{ctx.author.display_name} is a *fucking legend* and hit **another** yahtzee. +100!")

                await ctx.channel.send(f"{ctx.author.display_name} scored {score['score']} points!")
                self.ongoingGame.changeScore(ctx.author.id, score['score'])
                self.ongoingGame.gameState['players'][ctx.author.id]['alreadyScored'][category] = score['score']
                self.ongoingGame.nextTurn()
                self.ongoingGame.gameState['timesRolled'] = 0
                if await self.checkIfOver(ctx):
                    return
                await ctx.channel.send(f"{self.ongoingGame.whoseTurn()} it's your turn bud.")
            else:
                await ctx.channel.send('Do you even know how to play this fucking game?')

    async def calculateScore(self, category):
        if category == 'ones':
            return {'score':self.ongoingGame.gameState['rolls'].count(1) * 1}
        elif category == 'twos':
            return {'score':self.ongoingGame.gameState['rolls'].count(2) * 2}
        elif category == 'threes':
            return {'score':self.ongoingGame.gameState['rolls'].count(3) * 3}
        elif category == 'fours':
            return {'score':self.ongoingGame.gameState['rolls'].count(4) * 4}
        elif category == 'fives':
            return {'score':self.ongoingGame.gameState['rolls'].count(5) * 5}
        elif category == 'sixes':
            return {'score':self.ongoingGame.gameState['rolls'].count(6) * 6}
        elif category == '3x':
            return self.determine3x()
        elif category == '4x':
            return self.determine4x()
        elif category == 'full':
            return self.determineFull()
        elif category == 'small':
            return self.determineSmall()
        elif category == 'large':
            return self.determineLarge()
        elif category == '5x':
            return self.determine5x()
        elif category == 'chance':
            return {'score': sum(self.ongoingGame.gameState['rolls'])}

    def determine3x(self):
        for r in self.ongoingGame.gameState['rolls']:
            if self.ongoingGame.gameState['rolls'].count(r) >= 3:
                return {'score': sum(self.ongoingGame.gameState['rolls'])} 
        return {'score': 0}
    
    def determine4x(self):
        for r in self.ongoingGame.gameState['rolls']:
            if self.ongoingGame.gameState['rolls'].count(r) >= 4:
                return {'score': sum(self.ongoingGame.gameState['rolls'])} 
        return {'score': 0}

    def determineFull(self):
        small = False
        big = False
        for r in self.ongoingGame.gameState['rolls']:
            if self.ongoingGame.gameState['rolls'].count(r) == 3:
                big = True
            elif self.ongoingGame.gameState['rolls'].count(r) == 2:
                small = True
        if big and small:
            return {'score': 25}
        return {'score': 0}

    def determineSmall(self):
        longestStreak = 1
        lastDie = 0
        for r in sorted(self.ongoingGame.gameState['rolls']):
            if r - lastDie == 1:
                longestStreak += 1
                if longestStreak >= 4:
                    return {'score': 30}
            elif r - lastDie == 0:
                continue
            else:
                longestStreak = 1
            lastDie = r
        
        return {'score': 0}

    def determineLarge(self):
        longestStreak = 1
        lastDie = 0
        for r in sorted(self.ongoingGame.gameState['rolls']):
            if r - lastDie == 1:
                longestStreak += 1
                if longestStreak == 5:
                    return {'score': 30}
            elif r - lastDie == 0:
                continue
            else:
                longestStreak = 1
            lastDie = r
        return {'score': 0}

    def determine5x(self):
        for r in self.ongoingGame.gameState['rolls']:
            if self.ongoingGame.gameState['rolls'].count(r) >= 5:
                return {'score': 50}
        return {'score': 0}

    async def canPlay(self, ctx):
        if not self.ongoingGame:
            await ctx.channel.send('There isn\'t even a fucking game going.')
            return False
        if not self.ongoingGame.isPlaying(ctx.author.id):
            await ctx.channel.send('You aren\'t even in this game you dumb fuck.')
            return False
        elif not self.ongoingGame.isTurn(ctx.author.id):
            await ctx.channel.send('Its not your fucking turn.')
            return False
        return True

    async def checkIfOver(self, ctx):
        await ctx.channel.send(self.scoreMessage())
        if self.ongoingGame.currentTurn == 26:
            await ctx.channel.send('game over')
            winner = None
            score = 0
            for player in self.ongoingGame.players:
                if self.getBonusScore(ctx.author.id) > 62:
                    self.ongoingGame.changeScore(ctx.author.id, 35)
                    await ctx.channel.send(f"{ctx.author.display_name} hit the bonus! +35!")
                if self.ongoingGame.players[player]['score'] > score:
                    winner = player
            if winner is None:
                await ctx.channel.send('You idiots tied lmao')
            else:
                await ctx.channel.send(f'<@!{winner}> is simply too good.')
            self.ongoingGame = None
            return True
        return False
    
    def scoreMessage(self):
        playerScores = []
        
        for player in self.ongoingGame.players:
            msg = []
            for category in self.waysToScore:
                if category == 'BONUS':
                    msg.append(f"{'[' + category.title() + ']':8}{self.getBonusScore(player):^5}")
                else:
                    msg.append(f"{'[' + category.title() + ']':8}{self.getScore(player, category):^5}")
            playerScores.append(msg)

        out = []
        out.append('```ini\n\n')
        m = []
        for player in self.ongoingGame.players:
            m.append(f"[[{self.bot.get_user(player).display_name:^25}]]")  
        out.append('   |   '.join(m))
        out.append('')
        for i in range(7):
            m = []
            for player in range(len(playerScores)):
                m.append(f"{playerScores[player][i]}   {playerScores[player][i+7]}")
            out.append('   |   '.join(m))
        
        out.append('\n```')
        return '\n'.join(out)

    def getScore(self, playerID, category):
        return self.ongoingGame.gameState['players'][playerID]['alreadyScored'][category] if category in self.ongoingGame.gameState['players'][playerID]['alreadyScored'] else ' '
    
    def getBonusScore(self, playerID):
        categories = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
        total = 0
        for category in categories:
            total += self.getScore(playerID, category) if self.getScore(playerID, category) != ' ' else 0
        return total

class Game():
    players = None
    numPlayers = None
    game = None
    currentTurn = None
    accepted = None
    gameState = None

    def __init__(self, game, players, gameState = {}):
        self.numPlayers = 0
        self.players = {}
        #players is a tuple of tuples for god knows what reason
        for player in players:
            self.players[player] = {'score': 0, 'id': self.numPlayers}
            self.numPlayers += 1
        self.game = game
        #self.currentTurn = random.randint(0, self.numPlayers-1)
        self.currentTurn = 0  # The person that got challenged is always the 0th players. Make them first player so they can make a move to accept the game
        self.accepted = False
        self.gameState = gameState
    
    def isPlaying(self, playerID):
        for player in self.players:
            if playerID == player:
                return True
        return False

    def isTurn(self, playerID):
        for player in self.players:
            if self.players[player]['id'] == self.currentTurn % self.numPlayers and playerID == player:
                return True
        return False

    def whoseTurn(self):
        for player in self.players:
            if self.players[player]['id'] == self.currentTurn % self.numPlayers:
                return f'<@!{player}>'

    def nextTurn(self):
        self.currentTurn = self.currentTurn + 1

    def changeScore(self, playerID:int, score):
        self.players[playerID]['score'] += score
    
    def accept(self):
        self.accepted = True