import discord
from discord.ext.commands import Bot
from discord.ext import commands

import random
import shutil
from insults import insult


class Utils(commands.Cog):
    helpstring = []
    helpEmoji = '🔧'
    roles = {}
    msgs = [704922924091441183, 705216156352643082]
    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!audit; shows latest entries in the audit log')
        with open('/home/pi/workspace/Botty/deps/roles.txt', 'r') as f:
            for l in f.readlines():
                e = l.split(' ')
                self.roles[e[0]] = e[1].replace('\n', '')

    @commands.command(pass_context=True)
    async def audit(self, ctx, number=10):
        msg = []
        async for e in ctx.message.guild.audit_logs(limit=int(number)):
            act = str(e.action).split('.')[-1]
            msg.append(f'{e.user}: {act} {e.target}')
        await ctx.channel.send('\n'.join(msg))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.msgs:
            guild = self.bot.get_guild(payload.guild_id)
            mem = await guild.fetch_member(payload.user_id)
            role = discord.utils.get(guild.roles, name=self.roles[payload.emoji.name])
            await mem.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in self.msgs:
            guild = self.bot.get_guild(payload.guild_id)
            mem = guild.get_member(int(payload.user_id))
            role = discord.utils.get(guild.roles, name=self.roles[payload.emoji.name])
            await mem.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        #chn = self.bot.get_channel(704901570617409600)
        #gld = self.bot.get_guild(704901570617409597)
        print(member)
        if member.guild.system_channel:
            await member.guild.system_channel.send(f'Welcome {member.mention}. {insult()}')
        if member.guild.id == 704901570617409600:
            role = discord.utils.get(gld.roles, name='Citizen')
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        chn = self.bot.get_channel(704901570617409600)
        if member.guild.system_channel:
            await member.guild.system_channel.send(f'Welcome {member.mention}. {insult()}')

    @commands.command(pass_context=True)
    async def role(self, ctx, emoji, role, msg=0):
        with open('/home/pi/workspace/Botty/deps/roles.txt', 'a') as f:
            f.write(f'{emoji} {role}\n')
        self.roles[emoji] = role

        await ctx.message.guild.create_role(name=role, mentionable=True)
        roleChannel = ctx.channel.guild.get_channel(704904460576751698)
        rtnMsg = await roleChannel.fetch_message(self.msgs[msg])
        await rtnMsg.add_reaction(emoji)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def addColor(self, ctx, *emojis):
        for em in emojis:
            roleChannel = ctx.channel.guild.get_channel(704904460576751698)
            rtnMsg = await roleChannel.fetch_message(705216156352643082)
            await rtnMsg.add_reaction(em)

    @commands.command(pass_context=True)
    async def addOther(self, ctx, *emojis):
        for em in emojis:
            roleChannel = ctx.channel.guild.get_channel(704904460576751698)
            rtnMsg = await roleChannel.fetch_message(704922924091441183)
            await rtnMsg.add_reaction(em)

    @commands.command(pass_context=True)
    async def removeRole(self, ctx, msg=0, *emojis):
        for em in emojis:
            roleChannel = ctx.channel.guild.get_channel(704904460576751698)
            rtnMsg = await roleChannel.fetch_message(self.msgs[msg])
            await rtnMsg.clear_reaction(em)

    @commands.command(pass_context=True)
    async def update(self, ctx, emoji, newEmoji, newRole):
        global roles
        roles = {}
        with open('/home/pi/workspace/Botty/deps/temp.txt', 'w') as fout:
            with open('/home/pi/workspace/Botty/deps/roles.txt', 'r') as f:
                for l in f.readlines():
                    data = l.replace('\n', '').split(' ')
                    if data[0] == emoji:
                        fout.write(f'{newEmoji} {newRole}\n')
                        self.roles[newEmoji] = newRole
                        guild = ctx.message.guild
                        role = discord.utils.get(guild.roles, name=data[1])
                        mems = role.members
                        await role.delete()
                        rtnRole = await ctx.message.guild.create_role(name=newRole, mentionable=True)
                        for mem in mems:
                            await mem.add_roles(rtnRole)
                    else:
                        fout.write(f'{data[0]} {data[1]}\n')
                        self.roles[data[0]] = data[1]

        shutil.copyfile('/home/pi/workspace/Botty/deps/temp.txt', '/home/pi/workspace/Botty/deps/roles.txt')
        await ctx.message.delete()
