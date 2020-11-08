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
    send('5')
except:
    print('Connection not established. Restart Botty if you care')