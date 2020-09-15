import discord
from discord.ext.commands import Bot
from discord.ext import commands


from bs4 import BeautifulSoup
import requests
import urllib.request
import processing
import PIL
import asyncio
import googlesearch
import random
class Memes(commands.Cog):
    helpstring = []
    helpEmoji = '🆘'

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!corona')
        self.helpstring.append('!!eatbugs')
        self.helpstring.append('!!snurg')
        self.helpstring.append('!!fm')
        self.helpstring.append('!!deepfry (df)')

    @commands.command(pass_context=True)
    async def eatbugs(self, ctx):
        embed = discord.Embed(title="Eat", description="Bugs", color=0x00ff00)
        embed.set_image(url="https://cdn.discordapp.com/attachments/367376649857269760/702664825360089173/bug.jpg")
        await ctx.channel.send(embed=embed)

    @commands.command(pass_context=True)
    async def corona(self, ctx):
        url = f'https://www.worldometers.info/coronavirus/'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        nums = soup.find_all(class_='maincounter-number')
        cases = nums[0].text.replace(' ', '').replace('\n', '')
        deaths = nums[1].text.replace(' ', '').replace('\n', '')
        recovered = nums[2].text.replace(' ', '').replace('\n', '')

        if ctx.message.author.id == 194250346883842048:
            await ctx.channel.send(f"Hey {ctx.message.guild.get_member(194250346883842048).mention}, {deaths} have fucking DIED :skull:")
        else:
            msg = ["```ini"]
            msg.append(f'[Cases] {cases}')
            msg.append(f'[Deaths] {deaths}')
            msg.append(f'[Recovered] {recovered}')
            msg.append('```')
            await ctx.channel.send('\n'.join(msg))

    @commands.command(pass_context=True)
    async def brrbrrbrrrrrrr(self, ctx):
        await ctx.channel.send('Waiting...')
        url = 'https://www.worldometers.info/coronavirus/'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        nums = soup.find_all(class_='maincounter-number')
        cases = nums[0].text.replace(' ', '').replace('\n', '').replace(',', '')

        while(1):
            if(int(cases) >= 3000000):
                msg = []
                msg.append(f"{ctx.message.guild.get_member(194250346883842048).mention} {ctx.message.guild.get_member(175732928586842113).mention} {ctx.message.guild.get_member(196467600048390155).mention} {ctx.message.guild.get_member(209120745610149890).mention}")
                msg.append(f"{ctx.message.guild.get_member(194250346883842048).mention} {ctx.message.guild.get_member(141807553158840320).mention} {ctx.message.guild.get_member(687787885939916801).mention} {ctx.message.guild.get_member(120040589558415360).mention}")
                msg.append(f":postal_horn: :postal_horn: :postal_horn: :postal_horn: :postal_horn: BRR BRRR BRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR <:dootdoot:449609778486968321> <:dootdoot:449609778486968321> <:dootdoot:449609778486968321> <:dootdoot:449609778486968321> <:dootdoot:449609778486968321> <:dootdoot:449609778486968321>")
                msg.append(f"<:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418>3,000,000 HAVE BEEN FUCKIN INFECTED <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418> <:snurg:663246769450385418>")
                await ctx.channel.send('\n'.join(msg))
                return
            else:
               await asyncio.sleep(60 * 5)

    @commands.command(pass_context=True)
    async def snurg(self, ctx):
        if ctx.channel.name is "botcrepe":
            while(False):
                await ctx.channel.send('<:snurg:663246769450385418>')
                await asyncio.sleep(6)

        await ctx.channel.send('<:snurg:663246769450385418>')

    @commands.command(pass_context=True)
    async def ping(self, ctx, member: discord.Member = None, msg: str = "SHIT"):
        if member is None:
            await ctx.channel.send("Pong!")
        else:
            await ctx.channel.send("WAKE THE FUCK UP " + member.mention + " AND GET READY TO DO SOME " + msg)

    @commands.command(pass_context=True)
    async def fm(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.channel.send(":postal_horn: :postal_horn: :postal_horn: " + ctx.message.author.mention + " YOU HAVE BEEN FUCKIN MURDERED <:dootdoot:449609778486968321> <:dootdoot:449609778486968321> <:dootdoot:449609778486968321>")
        else:
            await ctx.channel.send(":postal_horn: :postal_horn: :postal_horn: " + member.mention + " YOU HAVE BEEN FUCKIN MURDERED <:dootdoot:449609778486968321> <:dootdoot:449609778486968321> <:dootdoot:449609778486968321>")


    @commands.command(pass_context=True)
    async def bing(self, ctx, *query):
        rtn = None
        for url in googlesearch.search(' '.join(query), tld='com', lang='en', num=1, start=6, stop=7, pause=2.0):
            rtn = url
            break
        
        res = requests.get(url)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.find_all(text=True)

        output = []
        blacklist = [
            '[document]',
            'noscript',
            'header',
            'html',
            'meta',
            'head', 
            'input',
            'script',
            'style',
            # there may be more elements you don't want, such as "style", etc.
        ]

        for t in text:
            if t.parent.name not in blacklist:
                output.append(t.replace('\n', ''))
        output = list(filter(None, output))
        output = ' '.join(output)
        await ctx.channel.send(output[:1999])
        

    @commands.command(pass_context=True)
    async def df(self, ctx, img=None, flares=True):
        await self.deepfry(ctx, img, flares)

    @commands.command(pass_context=True)
    async def deepfry(self, ctx, img=None, flares=True):
        img_src = '/home/pi/Botty/downloads/df_src.png'
        img_temp = '/home/pi/Botty/downloads/df_temp.jpeg'
        img_out = '/home/pi/Botty/downloads/df.jpeg'
        url = None
        
        url = await self.findImage(ctx, img)

        if not url:
            return

        response = requests.get(url)
        if response.status_code == 200:
            with open(img_src, 'wb') as f:
                f.write(response.content)

        img = PIL.Image.open(img_src)

        img = img.convert('RGB')
        await asyncio.sleep(.01)
        img = await processing.crushAndBack(img)
        img = await processing.generateHue(img)

        rtn = await processing.addFlare(img, img_src)
        img = rtn[0]
        found = rtn[1]
        
        #Fix Eye Flares when you feel like actually figuring something out
        while(False):
            print('looping')
            img.save(img_temp, 'jpeg')
            rtn = await processing.addFlare(img, img_temp)
            img = rtn[0]
            found = rtn[1]
        
        img.save(img_out, 'jpeg')   

        await ctx.channel.send(file=discord.File(img_out))

    @commands.command(pass_context=True)
    async def eb(self, ctx, *args):
        await self.eightball(ctx, *args)
        
    @commands.command(pass_context=True)
    async def eightball(self, ctx, *args):
        answers = ["Fuck yeah!", "Of course, you donkey", "Calculating.......\nOutlook good", "You may rely on it", "My programmer sucks, try again later", "Out to Lunch", "What do I look like, the bot with all the answers?", "Hell no you dolt", "CIA says: No"]
        await ctx.channel.send(random.choice(answers))


    @commands.command(pass_context=True)
    async def meme(self, ctx, *args):
        img_src = '/home/pi/Botty/downloads/meme_src.png'
        img_out = '/home/pi/Botty/downloads/meme.jpeg'

        url = None

        if 'http' in args[0]:
            url = args[0]
            args = args[1:]

        if not url:
            url = await self.findImage(ctx, 'nothere')

        if not url:
            return

        response = requests.get(url)
        if response.status_code == 200:
            with open(img_src, 'wb') as f:
                f.write(response.content)

        img = PIL.Image.open(img_src)
        text = ' '.join(args)
        print(text)
        if text.startswith('|'):
            top = ''
            bot = text.split('|')[1]
        elif text.endswith('|'):
            top = text.split('|')[0]
            bot = ''
        else:
            text = text.split('|')
            top = text[0]
            bot = text[1]
        top = top.strip()
        bot = bot.strip()
        draw = PIL.ImageDraw.Draw(img)
        w = img.width
        font = PIL.ImageFont.truetype("/home/pi/.fonts/pressuru.otf", int(w * .075))

        # Please dont ask  
        rtn = await processing.drawText(img, draw, font, top, "top")
        rtn[1] = list(filter(lambda _: _ != '', rtn[1]))
        for i in range(0, len(rtn[1])):
            w, h = draw.textsize(rtn[1][i], font)
            x = img.width/2 - w/2
            y = rtn[2] + h + 15 + (h * 1.5 * i)

            draw.text((x-2, y-2), rtn[1][i],(0,0,0),font=font)
            draw.text((x+2, y-2), rtn[1][i],(0,0,0),font=font)
            draw.text((x+2, y+2), rtn[1][i],(0,0,0),font=font)
            draw.text((x-2, y+2), rtn[1][i],(0,0,0),font=font)
            draw.text((x, y), rtn[1][i], (255,255,255), font=font)
            lastY = y
        
        # Just dont
        rtn = await processing.drawText(img, draw, font, bot, "bottom")
        rtn[1] = list(filter(lambda _: _ != '', rtn[1]))

        lastY = 0
        for i in range(0, len(rtn[1])):
            w, h = draw.textsize(rtn[1][i], font)
            x = img.width/2 - w/2
            y = rtn[2] + h + (h * 1.5 * i)
            draw.text((x-2, y-2), rtn[1][i],(0,0,0),font=font)
            draw.text((x+2, y-2), rtn[1][i],(0,0,0),font=font)
            draw.text((x+2, y+2), rtn[1][i],(0,0,0),font=font)
            draw.text((x-2, y+2), rtn[1][i],(0,0,0),font=font)
            draw.text((x, y), rtn[1][i], (255,255,255), font=font)

            lastY = y
        
        img.save(img_out, 'jpeg')

        await ctx.channel.send(file=discord.File(img_out))

    async def findImage(self, ctx, img):
        url = None
        try:
            if img:  # Check if image is given in command
                if 'http' in img:
                    url = ctx.message.content.split(' ')[1]
                else:
                    raise Exception('Gotta Fail somehow')
            else:  # Is it attached to command?
                url = ctx.message.attachments[0].url
        except:
            async for msg in ctx.channel.history(limit=50):
                try:  # Go through history until we find an image
                    if(msg.embeds):  # Is it embeded?
                        url = msg.embeds[0].url  # Could be a url changed to an embed
                        if('Embed.Empty' in str(url)):
                            url = msg.embeds[0].image.url  # If its not, then its am actual embeded image
                        break
                    url = msg.attachments[0].url  # None of those? Could be attachment
                    break
                except:  #  all of that failed so no image in that message
                    pass
        if url is None:
            await ctx.channel.send('Could not find an image')
            return None
        return url
