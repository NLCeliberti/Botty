import discord
from discord.ext.commands import Bot
from discord.ext import commands

import cv2
from sklearn.cluster import MiniBatchKMeans
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import subprocess
#from led import send, EC

import zmq
import zlib
import pickle
import requests

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.4:5555")

class leds(commands.Cog):
    helpstring = []
    helpEmoji = '🚥'

    def __init__(self, bot):
        self.bot = bot
        self.helpstring.append('!!led &number *rgb ; Control Nick\'s LEDs')
        self.helpstring.append('!!pixel *url ; Send a url or an image to pixelate')

        
    @commands.command(pass_context=True)
    async def led(self, ctx, typ, *rgb):
        rtn = send(typ)
        if(rtn == 'Leds are cool'):
            await ctx.message.delete()
        else:
            await ctx.channel.send(rtn)
        '''
        if(len(rgb) > 3):
            await ctx.channel.send('Thats a bad message 1')
            return
        elif(len(rgb) == 3):
            for m in rgb:
                try:
                    int(m)
                except ValueError:
                    await ctx.channel.send('Thats a bad message 2')
                    return
        msg = ' '.join(rgb)
        rtn = send(typ + ' ' + msg)
        if(rtn == 'Leds are cool'):
            await ctx.message.delete()
        else:
            await ctx.channel.send(rtn)
        '''

    @commands.command(pass_context=True)
    async def resetSerial(self, ctx):
        if ctx.message.author.id == '175732928586842113':
            led.EC()
        else:
            await ctx.channel.send('Fuck off')

    @commands.command(pass_context=True)
    async def pixel(self, ctx, img=None):
        img_src = '/home/pi/workspace/Botty/downloads/pixel_src.png'
        img_out = '/home/pi/workspace/Botty/downloads/pixeled.png'
        if img:
            url = ctx.message.content.split(' ')[1]
        else:
            url = ctx.message.attachments[0].url

        response = requests.get(url)
        if response.status_code == 200:
            with open(img_src, 'wb') as f:
                f.write(response.content)


        with open(img_src, 'rb') as f:
            self.send_zipped_pickle(socket, f.read())
        await ctx.channel.send(file=discord.File(img_src))
        message = socket.recv()

        return
        # Open input image in BGR space
        im_in = cv2.imread(img_src, cv2.IMREAD_COLOR)

        # Process image with given arguments
        im_out = self.process_frame(im_in, 32, 64, 16, None)

        # Write output (or display output image, depending on usage)
        cv2.imwrite(img_out, im_out)

        with open(img_out, 'rb') as f:
            self.send_zipped_pickle(socket, f.read())
        await ctx.channel.send(file=discord.File(img_out))
        message = socket.recv()
        
        #await ctx.channel.send('img currently disabled')
        #Qsubprocess.Popen(['sudo', 'python3', '/home/pi/workspace/Botty/imports/img.py'])
    #    image = Image.open(img_out)
    #
    #    # Configuration for the matrix
    #    options = RGBMatrixOptions()
    #    options.rows = 32
    #    options.chain_length = 1
    #    options.parallel = 1
    #    options.brightness = 25
    #    options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
    #
    #    matrix = RGBMatrix(options = options)
    #
    #    # Make image fit our screen.
    #    image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
    #
    #    matrix.SetImage(image.convert('RGB'))
    #    time.sleep(10)
    #    del matrix

    def send_zipped_pickle(self, socket, obj, flags=0, protocol=-1):
        """pickle an object, and zip the pickle before sending it"""
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return socket.send(z, flags=flags)

    def process_frame(self, im, width, height, n_clusters=16, prescale_size=None):
        h, w = im.shape[:2]

        # Apply optional prescale to source image
        if prescale_size is not None:
            im = cv2.resize(im, prescale_size, interpolation=cv2.INTER_LINEAR)

        # Quantize (cluster colors) and resample (subsample+supersample)
        return self.im_resample(self.im_quantize(im, n_clusters), width, height, w, h)

    def im_resample(self, im, subsample_width, subsample_height, resample_width, resample_height):
        # Subsample to pixelate
        im_subsample = cv2.resize(im, (subsample_width, subsample_height), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(im_subsample, (resample_width, resample_height), interpolation=cv2.INTER_NEAREST)

    def im_quantize(self, im, n_clusters):
        h, w = im.shape[:2]

        # Convert the image from the BGR color space to the L*a*b* color space.
        # Since we will be clustering using k-means which is based on the euclidean
        # distance, we'll use the L*a*b* color space where the euclidean distance
        # implies perceptual meaning
        im_colorspace = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)

        # - Reshape the image into a feature vector so that k-means can be applied
        # - Apply k-means using the specified number of clusters and then
        #   create the quantized image based on the predictions
        clt = MiniBatchKMeans(n_clusters=n_clusters)
        labels = clt.fit_predict(im_colorspace.reshape((w * h, 3)))
        im_quant_colorspace = clt.cluster_centers_.astype(np.uint8)[labels].reshape((h, w, 3))

        # Convert from L*a*b* back to BGR
        return cv2.cvtColor(im_quant_colorspace, cv2.COLOR_LAB2BGR)


import serial
import struct
from color import colors
from random import *
ser = None

typeList = {'Reset': 0,
            'Add': 1,
            'Solid': 2,
            'Snake': 3,
            'Splits': 4,
            'Murica': 5,
            'Rave': 6,
            'Rainbow': 7,
            'White': 8,
            'Off': 9
           }

def EC():
    global ser
    got = ser.read()
    print('Established Connection: ' + got.decode("utf-8"))

def send(inp):
    global ser
    msg = makeByteMsg(inp)
    if type(msg) is bytes:
        ser.write(msg)
        return('Leds are cool')
    elif type(msg) is str:
        return(msg)
    else:
        return('God knows what happened')


def makeByteMsg(inp):
    msg = ''
    arr = inp.split(' ')
    out = []
    try:
        out.append(int(arr[0]))
    except ValueError:
        if(arr[0] in typeList):
            out.append(typeList[arr[0]])
        else:
            return 'bad type word'
    if(out[0] == 1):
        if(len(arr) < 2):
            return 'said to add color but no color'

        #Get rgb color
        if(len(arr) <= 2):
            if(arr[1] in colors):
                clr = colors[arr[1]]
                clrA = clr.split(',')
                out.append(int(clrA[0]))
                out.append(int(clrA[1]))
                out.append(int(clrA[2]))
            else:
                return 'bad color word'
        elif len(arr) == 4:
            try:
                out.append(int(arr[1]))
                out.append(int(arr[2]))
                out.append(int(arr[3]))
            except ValueError:
                return 'color not rgb'
        else:
            return 'Bad input length'
    if(out[0] >= len(typeList)):
        return 'bad type 2'
    #Turn into bytes
    if(len(out) == 1):
        msg = struct.pack('>1B', out[0])
    elif len(out) == 4:
        msg = struct.pack('>4B', out[0], out[1], out[2], out[3])

    return(msg)

#msg = '1 ' + str(randint(0,255)) + ' ' + str(randint(0,255)) + ' ' + str(randint(0,255))
#print(msg)



try:
    # read from Arduino
    ser = serial.Serial('/dev/ttyUSB0',9600)
    got = ser.read()
    print('Established Connection: ' + got.decode("utf-8"))
    send('5')
except Exception as e:
    with open('/home/pi/workspace/Botty/logs/error.err', 'a') as f:
        f.write(f"{e}\n")
    print('Connection not established. Restart Botty if you care')