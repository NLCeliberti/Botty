import discord
from discord.ext.commands import Bot
from discord.ext import commands

import r6sapi

class r6(commands.Cog):
    helpstring = []
    helpEmoji = '🌈'
    auth = None

    def __init__(self, bot):
        self.bot = bot
        self.auth = self.r6auth()
        self.helpstring.append('!!r6s &playerName ; Returns stats for the given player')
        self.helpstring.append('!!op &playerName &operatorName ; Returns stats for given operator')

    @commands.command(pass_context=True)
    async def r6s(self, ctx, player):
        '''!r6s player optional(queue)'''
        msg = await self.playerStats(player)
        if msg is None:
            return('Player not found')

        out = ['```ini\n']
        for m in msg:
            out.append('[ ' + m[0] + ' ]' + ' ' + str(m[1]))
        out.append('\n```')
        await ctx.channel.send('\n'.join(out))

    @commands.command()
    async def op(self, player, op):
        msg = await self.getOp(player, op)
        if msg is None:
            await ctx.channel.send('Error')
            return
        out = ['```ini\n']
        for m in msg:
            out.append('[ ' + m[0] + ' ]' + ' ' + str(m[1]))
        out.append('\n```')
        await ctx.channel.send('\n'.join(out))

#    @bot.command(pass_context=True)
#    async def r6sMatch(ctx, imgurLink: str):
#        urllib.request.urlretrieve(imgurLink, 'match.png')
#        im = Image.open('match.png')  # the second one
#        #enhancer = ImageEnhance.Contrast(im)
#        #im = enhancer.enhance(100)
#        #im = im.convert('LA')
#        if im.mode == 'RGBA':
#            r, g, b, a = im.split()
#            rgb_image = Image.merge('RGB', (r, g, b))
#            inverted_image = PIL.ImageOps.invert(rgb_image)
#            r2, g2, b2 = inverted_image.split()
#            final_transparent_image = Image.merge('RGBA', (r2, g2, b2, a))
#            final_transparent_image.save('new_name.png')
#        else:
#            inverted_image = PIL.ImageOps.invert(im)
#            inverted_image.save('new_name.png')
#
#        text = pytesseract.image_to_string(Image.open('new_name.png'))
#
#        names = text.split('\n')
#        for name in names:
#            if (len(name) > 2):
#                await ctx.channel.send(await getPlayer(name))

    async def getPlayer(self, playerName):
        msg = await self.rankedStats(playerName)
        if msg is None:
            return('Player not found: ' + playerName)

        out = ['```ini\n']
        for x in range(int(len(msg) / 2)):
            out.append('{} {}'.format(('[ ' + msg[x][0] + ' ]' + ' ' + str(msg[x][1])).ljust(
                35), ('[ ' + msg[x + int(len(msg) / 2)][0] + ' ]' + ' ' + str(msg[x + int(len(msg) / 2)][1]))))
        out.append('\n```')
        return('\n'.join(out))

    def r6auth(self):
        if self.auth is None or self.auth.session.closed:
            with open('/home/pi/Botty/deps/r6_secret.txt', 'r') as f:
                for l in f:
                    t = l.split(' ')
                    email = t[0]
                    p = t[1].strip()
            self.auth = r6sapi.Auth(email, p, None, None, 120, 1)

    async def playerStats(self, player):
        self.r6auth()
        stat = await self.auth.get_player(player, r6sapi.Platforms.UPLAY)
        await stat.check_general()
        await stat.check_queues()
        if (stat is None):
            return None
        out = []
        out.append([player.title(), ('Casual | Ranked')])
        out.append(['Kills', '{} | {}'.format(stat.kills, stat.ranked.kills)])
        out.append(['Deaths', '{} | {}'.format(stat.deaths, stat.ranked.deaths)])
        out.append(['KD', '{:.3f} | {:.3f}'.format(float(stat.kills) / float(stat.deaths if stat.deaths != 0 else 1), float(stat.ranked.kills) / float(stat.ranked.deaths if stat.ranked.deaths != 0 else 1))])
        out.append(['Assists', stat.kill_assists])
        out.append(['Playtime', '{:.1f}h'.format(stat.time_played / 60 / 60)])
        out.append(['Record', '{} - {} | {} - {}'.format(stat.matches_won,
                                                         stat.matches_lost, stat.ranked.won, stat.ranked.lost)])
        out.append(['Win %', '{:.3f} | {:.3f}'.format(float(stat.matches_won) / float(stat.matches_lost + stat.matches_won) if float(stat.matches_lost + stat.matches_won)
                                                      != 0 else 1, float(stat.ranked.won) / float(stat.ranked.lost + stat.ranked.won) if float(stat.ranked.lost + stat.ranked.won) != 0 else 1)])
        out.append(['Revives', stat.revives])
        out.append(['Melees', stat.melee_kills])
        out.append(['Bullets Hit', stat.bullets_hit])
        out.append(['Bullets Fired', stat.bullets_fired])
        out.append(['Accuracy', '{:.2f}%'.format((float(stat.bullets_hit) / float(
            stat.bullets_fired) if float(stat.bullets_fired) != 0 else 1) * 100)])
        out.append(['Headshots', stat.headshots])
        out.append(['Penetractions', stat.penetration_kills])
        return out

    async def rankedStats(self, player):
        self.r6auth()
        stat = await self.auth.get_player(player, r6sapi.Platforms.UPLAY)
        await stat.check_general()
        await stat.check_queues()
        if (stat is None):
            return None
        out = []
        out.append([player.title(), ('Ranked')])
        out.append(['Kills', '{}'.format(stat.ranked.kills)])
        out.append(['Deaths', '{}'.format(stat.ranked.deaths)])
        out.append(['KD', '{:.3f}'.format(float(stat.ranked.kills) /
                                          float(stat.ranked.deaths if stat.ranked.deaths != 0 else 1))])
        out.append(['Playtime', '{:.1f}h'.format(stat.time_played / 60 / 60)])
        out.append(['Record', '{} | {}'.format(stat.ranked.won, stat.ranked.lost)])
        out.append(['Win %', '{:.0f}%'.format((float(stat.ranked.won) / float(stat.ranked.lost +
                                                                              stat.ranked.won) * 100) if float(stat.ranked.lost + stat.ranked.won) != 0 else 1)])
        out.append(['Accuracy', '{:.2f}%'.format((float(stat.bullets_hit) / float(
            stat.bullets_fired) if float(stat.bullets_fired) != 0 else 1) * 100)])
        out.append(['Headshots', stat.headshots])
        out.append(['Penetractions', stat.penetration_kills])
        return out

    async def getOp(self, player, op):
        self.r6auth()
        play = await self.auth.get_player(player, r6sapi.Platforms.UPLAY)
        if (play is None):
            return None
        stat = await play.get_operator(op)
        if stat is None:
            return None
        try:
            out = []
            out.append([player.title(), op.title()])
            out.append(['Wins', stat.wins])
            out.append(['Losses', stat.losses])
            out.append(
                ['W/L %', '{:.2f}%'.format((float(stat.wins) / float(stat.wins + stat.losses)) * 100)])
            out.append(['Time Played', '{:.1f}h'.format(
                float(stat.time_played) / 60 / 60)])
            out.append(['Kills', stat.kills])
            out.append(['Deaths', stat.deaths])
            out.append(['KD', '{:.3f}'.format(stat.kills / stat.deaths)])
            out.append(['Headshots', stat.headshots])
            out.append(['Melees', stat.melees])
            out.append(['DBNOs', stat.dbnos])
            out.append([stat.statistic_name, stat.statistic])

            return out
        except:
            return None
