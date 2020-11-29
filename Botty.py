import discord
from discord.ext.commands import Bot, errors
from discord.ext import commands
import sys
import importlib
import random
import asyncio
sys.path.insert(1, '/home/pi/workspace/Botty/plugins')

plugins = []
with open('/home/pi/workspace/Botty/deps/plugins.txt', 'r') as f:
    for im in f.read().split(' '):
        plugins.append(im.strip())

modules = {}
for p in plugins:
    try:
        exec(f"import {p}")
    except Exception as e:
        print(e)

helpMsgs = [0,0,0,0,0]
helpMsgCount = 0
helpEmojis = {}

intents = discord.Intents.all()

bot_prefix = "!!"
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)
bot.remove_command('help')

commandsFile = '/home/pi/workspace/Botty/logs/commands.log'

@bot.event
async def on_ready():
    global helpEmojis
    for p in plugins:
        exec(f'helpEmojis[{p}.{p}.helpEmoji] = {p}.{p}.__name__')
    print("Bot Online!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    await bot.change_presence(activity=discord.Game(name='The result of liquor and depression'))
    

@bot.event
async def on_message(message):
    if '!!' in message.content[:2]:
        with open(commandsFile, 'a') as f:
            f.write(f'{message.author} || {message.content} \n')
    if(message.author.name == 'Friday'):
        if(message.embeds):
            if message.embeds[0].title== 'I PLAY POT OF GREED...':  # git.fucked
                await message.delete()

    elif(message.author.id == 147516466126651392 and '!!!!!' in message.content):  # if fly and !!!!!
        await message.add_reaction('❕')
        await message.add_reaction('🔫')
        await message.add_reaction('💀')
        await message.add_reaction('🌽')
        await message.channel.send('!!!!!!!!!!')
        await message.add_reaction('🦄')
        await message.add_reaction('🦡')
        await message.add_reaction('🐟')
        await message.add_reaction('❗')

    if ' && ' in message.content and message.content.startswith('!!'):
        cmds = message.content.split(' && ')
        for cmd in cmds:
            if not cmd.startswith('!!'):
                cmd = '!!' + cmd
            message.content = cmd
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)

for p in plugins:
    exec(f'bot.add_cog({p}.{p}(bot))')

@bot.command(pass_context=True)
async def reload(ctx, cog, newcog=False):
    if ctx.message.author.id == 175732928586842113:
        if not newcog:
            if cog in plugins:
                bot.remove_cog(cog)
                exec(f'importlib.reload({cog})')
                exec(f'bot.add_cog({cog}.{cog}(bot))')
                await ctx.message.add_reaction('👍')
            else:
                await ctx.channel.send('Cog not found')
        else:
            with open('/home/pi/workspace/Botty/deps/plugins.txt', 'a') as f:
                f.write(f' {cog}')
                exec(f'import {cog }')
                exec(f'bot.add_cog({cog}.{cog}(bot))')
                exec(f'helpEmojis[{im}.{im}.__name__] = {im}.{im}.helpEmoji')
                plugins.append(cog)
                await ctx.message.add_reaction('👍')
    else:
        await ctx.channel.send('fuk u')
'''
'''
@bot.event
async def on_command_error(ctx, error):
        if errors.CommandNotFound == type(error):
            pass
        elif errors.BadArgument == type(error):
            await ctx.channel.send(random.choice(['ay learn how to fucking read dumbass', 'There is a help menu ya know', 'The only person with a worse argument than you is antivaxers, idiot.']))
        else:
            await ctx.message.add_reaction('💀')
            nik = bot.get_user(175732928586842113)
            await nik.send(f'{ctx.message.guild} :: {ctx.message.channel} :: {ctx.message.author} ::: {ctx.message.content}\n{error}')
            await ctx.message.author.send(f'You have been reported to the authorities for botty fucking.\nError: {error}') 

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in helpMsgs:
        await helpMsgEdit(reaction.message, helpEmojis[reaction.emoji])

@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.message.id in helpMsgs:
        await helpMsgEdit(reaction.message, helpEmojis[reaction.emoji])
################################################################################
#								Help    									   #
################################################################################

@bot.command(pass_context=True)
async def help(ctx):
    out = []
    out.append(f'React with emojis to see the commands')
    msg = await ctx.channel.send('\n'.join(out))
    #emoji = bot.get_emoji(123456)
    for key in helpEmojis:
        await msg.add_reaction(f'{key}')
    await asyncio.sleep(3)
    addHelpMsg(msg.id)

async def helpMsgEdit(message, module):
    msg = []
    msg.append('```yaml\n')

    msg.append('# Anything with & is required')
    msg.append('# Anything with * is optional')
    msg.append('Anything in () is shorthand')
    exec(f'msg += {module}.{module}.helpstring')
    msg.append('\n```')
    await message.edit(content='\n'.join(msg))

'''
@bot.command(pass_context=True)
async def help(ctx):
    msg = []
    msg.append('```yaml\n')

    msg.append('# Anything with & is required')
    msg.append('# Anything with * is optional')
    msg.append('!!help ; This message you fucking idiot')
    for p in plugins:
        exec(f'msg += {p}.{p}.helpstring')
    msg.append('\n```')
    await ctx.channel.send('\n'.join(msg))
'''

def addHelpMsg(id):
    global helpMsgs
    global helpMsgCount
    helpMsgs[helpMsgCount % 5] = id
    helpMsgCount += 1

with open('/home/pi/workspace/Botty/deps/botty_secret.txt', 'r') as f:
    sekret = f.read()    
bot.run(sekret) #  Botty