import cv2
from PIL import Image, ImageOps, ImageEnhance, ImageFont, ImageDraw
import os
from imutils import face_utils
import dlib
import random
import asyncio

class Colors:
    RED = (254, 0, 2)
    YELLOW = (255, 255, 15)
    BLUE = (36, 113, 229)   
    WHITE = (255, 255, 255)
    

async def irisCoords(eye):
    #Finding the center point of the eye using the average outer extremes average of the eyes
    mid = (eye[0] +eye[3])/2
    mid = (int(mid[0]), int(mid[1]))
    return mid

async def generateHue(img):
    #Generating and increasing prominency of red band of the image
    img = img.convert('RGB')
    red = img.split()[0] #(R,G,B)
    await asyncio.sleep(.1)
    red = ImageEnhance.Contrast(red).enhance(2.0)
    red = ImageEnhance.Brightness(red).enhance(1.5)
    RANDOM = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    red = ImageOps.colorize(red, Colors.RED, RANDOM)
    await asyncio.sleep(.1)
    img = Image.blend(img, red, 0.77)
    #Keeping a 100% sharpness value for now, But would probably be better with a higher sharpness value
    img = ImageEnhance.Sharpness(img).enhance(150)
    return img

async def crushAndBack(img):
    img = img.convert('RGB')
    w,h = img.width, img.height
    img = img.resize((int(w ** .90), int(h ** .90)), resample = Image.LANCZOS)
    await asyncio.sleep(.05)
    img = img.resize((int(w ** .80), int(h ** .80)), resample = Image.BILINEAR)
    await asyncio.sleep(.05)
    img = img.resize((int(w ** .70), int(h ** .70)), resample = Image.BICUBIC)
    img = img.resize((w,h), resample = Image.BICUBIC)
    return img

async def addFlare(img, img_src):
    ''' Initialising dlib for frontal facial features '''
    flare = Image.open('/home/pi/workspace/Botty/downloads/flare.png')
    detect = dlib.get_frontal_face_detector()
    predict = dlib.shape_predictor("/home/pi/workspace/Botty/deps/shape_predictor_68_face_landmarks.dat")

    (lS, lE) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
    (rS, rE) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
    

    imgCv = cv2.imread(img_src)

    gray = cv2.cvtColor(imgCv, cv2.COLOR_BGR2GRAY)
    subjects = detect(gray, 0)

    leftEye = None
    rightEye = None
    await asyncio.sleep(.1)
    for subject in subjects:
        shape = predict(gray, subject)
        shape = face_utils.shape_to_np(shape)
        leftEye = shape[lS:lE]
        rightEye = shape[rS:rE]
    '''
        Assigning an area to paste the flare png Using the coordinates given by the Dlib module
        ln,rn is the distance between the top left and bottom right of the iris multiplied by 4.
        This is used to find the basic coordinates of the area in which the flare image will be pasted
    '''
    foundEye = False

    if(rightEye is not None):
        foundEye = True
        rn=(rightEye[4][0]-rightEye[0][0])*3
        rec2=(rightEye[1][0]-rn,rightEye[1][1]-rn)
        rec3=(rightEye[4][0]+rn,rightEye[4][1]+rn)
        areaRight=(rec2[0],rec2[1],rec3[0],rec3[1])
        flareRight=flare.resize((rec3[0]-rec2[0],rec3[1]-rec2[1]))
        img.paste(flareRight,areaRight,flareRight)
        
    if(leftEye is not None):
        foundEye = True
        ln=(leftEye[4][0]-leftEye[0][0])*3
        rec0=(leftEye[1][0]-ln,leftEye[1][1]-ln)
        rec1=(leftEye[4][0]+ln,leftEye[4][1]+ln)
        areaLeft=(rec0[0],rec0[1],rec1[0],rec1[1])
        flareLeft=flare.resize((rec1[0]-rec0[0],rec1[1]-rec0[1]))
        img.paste(flareLeft,areaLeft,flareLeft)

    return [img, foundEye]

async def drawText(img, draw, font, text, pos):
    DEBUG = False
    text = text.upper()
    w, h = draw.textsize(text, font) # measure the size the text will take
    lineCount = 1
    if w > img.width:
        lineCount = int(round((w / img.width) + 1))

    #print("lineCount: {}".format(lineCount))

    lines = []
    
    if lineCount > 1:

        lastCut = 0
        isLast = False
        for i in range(0,lineCount):
            if lastCut == 0:
                cut = int(len(text) / lineCount) * i
            else:
                cut = lastCut

            if i < lineCount-1:
                nextCut = int(len(text) / lineCount * (i+1) * 1.25)
                if DEBUG: print('am i even getting here     ' + str(nextCut))
            else:
                nextCut = len(text)
                isLast = True

            #print("cut: {} -> {}".format(cut, nextCut))

            # make sure we don't cut words in half
            if DEBUG: print(f'early    cut: {cut}     lc {lastCut}     nc {nextCut}')
            nextCut = min(nextCut, len(text))
            if nextCut == len(text) or text[nextCut] == " ":
                if DEBUG: print("may cut")
                if DEBUG: print(text)
                if DEBUG: print(len(text))
                if DEBUG: print(nextCut)
                pass
            else:
                #print("may not cut")
                try:
                    while text[nextCut] != " ":
                        nextCut -= 1
                except IndexError:
                    if DEBUG: print('indexerror')
                    pass
                #print("new cut: {}".format(nextCut))

            line = text[cut:nextCut].strip()

            # is line still fitting ?
            w, h = draw.textsize(line, font)
            if not isLast and w > img.width:
                if DEBUG: print("overshot")
                nextCut = min(nextCut - 1, len(text) - 1)
                try:
                    while text[nextCut] != " ":
                        nextCut -= 1
                except IndexError:
                    if DEBUG: print('indexerror')
                    pass
                    
                #print("new cut: {}".format(nextCut))

            if DEBUG: print(f'cut: {cut}     lc {lastCut}     nc {nextCut}')
            lastCut = nextCut
            lines.append(text[cut:nextCut].strip())
            if DEBUG: print(lines)

    else:
        lines.append(text)

        #print(lines)

    lastY = -h
    if pos == "bottom":
        lastY = img.height - h * (lineCount+1) - 10
    
    return [lineCount, lines, lastY]