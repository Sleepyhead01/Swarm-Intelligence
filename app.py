from flask import Flask, jsonify, abort, request, make_response, url_for,redirect,send_file
import sys
import numpy as np
from PIL import Image
import random
import time

img=None
botPose=[]
obstaclePose=[]
greenZone=[]
redZone=[]
originalGreenZone = []
mission_complete = False
score = 0
level = 0
numbots = 1

app = Flask(__name__, static_url_path = "")

@app.errorhandler(400)
def not_found1(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found2(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/', methods = ['GET'])
def getInfo():
    return redirect('/map')

@app.route('/score', methods=['GET'])
def getScore():
    global score
    return jsonify({'score': score})

@app.route('/level', methods=['GET'])
def getLevel():
    global level
    return jsonify({'level': level})

@app.route('/numbots', methods=['GET'])
def getnNumbots():
    global numbots
    return jsonify({'numbots': numbots})

@app.route('/map', methods = ['GET'])   #Hosts map at http://127.0.0.1:5000/map
def getMap():
    global img, numbots
    curr_img = np.copy(img)
    for botId in range(numbots):
        curr_img[botPose[botId][0]-3:min(botPose[botId][0]+3,200), botPose[botId][1]-3:min(botPose[botId][1]+3,200)] = np.array([0, 0, 255])
    im=Image.fromarray(curr_img)
    im.save("images/curr_map.png")
    return send_file('images/curr_map.png', mimetype='image/png',cache_timeout=-1)

@app.route('/botPose', methods = ['GET']) #Hosts botPose at http://127.0.0.1:5000/botPose and so on
def getBotPose():
    global botPose
    return jsonify(botPose)

@app.route('/obstaclesPose', methods = ['GET'])
def getObstaclePose():
    global obstaclePose
    return jsonify(obstaclePose)

@app.route('/greenZone', methods = ['GET'])
def getFinalPose():
    global greenZone
    return jsonify(greenZone)

@app.route('/missionComplete', methods = ['GET'])
def getMission():
    global mission_complete
    return jsonify(mission_complete)

@app.route('/redZone', methods=['GET'])
def getRedZone():
    global redZone
    return jsonify(redZone)

@app.route('/originalGreenZone', methods=['GET'])
def getOriginalGreenZone():
    global originalGreenZone
    return jsonify(originalGreenZone)

@app.route('/move', methods = ['GET'])
def move():
    global img, botPose,obstaclePose, mission_complete, score
    if mission_complete:
        return jsonify({'success': False, 'mission_complete': mission_complete})
    data=request.json
    if 'botId' not in data or 'moveType' not in data:
        abort(400)
    data['botId'] = int(data['botId'])
    data['moveType']=int(data['moveType'])
    if data['botId']<0 or data['botId']>len(botPose):
        abort(400)
    if data['moveType']<1 or data['moveType']>8:
        abort(400)
    if check_and_move(data['botId'], data['moveType']):
        botId=data['botId']
        img[botPose[botId][0], botPose[botId][1]] = np.array([150,150,220])
        score += check_mission(data['botId'])
        return jsonify({'success': True, 'mission_complete': mission_complete})
    else:
        return jsonify({'success': False, 'mission_complete': mission_complete})

@app.route('/set_new_map', methods = ['GET'])
def set_new_map():
    global score, mission_complete, botPose, img, obstaclePose, greenZone, redZone, level, numbots, originalGreenZone
    data=request.json
    img=None
    botPose=[]
    obstaclePose=[]
    greenZone=[]
    redZone=[]
    originalGreenZone = []
    mission_complete = False
    score = 0
    level = data['level'] 
    numbots = data['numbots']
    size1=200
    size2=40
    size=size2//2
    arr=[[0,0],[0,1],[1,0],[1,1]]
    random.seed(time.time())
    img=np.ones((size1,size1,3),dtype=np.uint8)*255
    xTop=0
    while xTop<size1:
        yTop=0
        while yTop<size1:
            num=random.randint(0,3)
            newX=xTop+arr[num][0]*(size2//2)
            newY=yTop+arr[num][1]*(size2//2)
            if (newX==0 and newY==0) or (newX==size1-(size2//2) and newY==size1-(size2//2)):
                pass
            else:
                # Single-objective environment
                if level == 1:
                    img[newX:newX+(size2//2),newY:newY+(size2//2),:]=np.zeros((size2//2,size2//2,3))
                    obstaclePose.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])

                # Multi-objective unconstrained environment
                elif level == 2 or level == 3 or level == 4:
                    if np.random.random() < 0.3:
                        img[newX:newX+(size2//2),newY:newY+(size2//2),:]=[0, 255, 0]
                        greenZone.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
                    else:
                        img[newX:newX+(size2//2),newY:newY+(size2//2),:]=np.zeros((size2//2,size2//2,3))
                        obstaclePose.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])

                # Multi-objective contrained environment
                else:
                    srand = np.random.random()
                    if srand < 0.3:
                        img[newX:newX+(size2//2),newY:newY+(size2//2),:]=[0, 255, 0]
                        greenZone.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
                    elif srand < 0.5:
                        img[newX:newX+(size2//2),newY:newY+(size2//2),:]=[255, 0, 0]
                        redZone.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
                    else:
                        img[newX:newX+(size2//2),newY:newY+(size2//2),:]=np.zeros((size2//2,size2//2,3))
                        obstaclePose.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
            yTop=yTop+size2
        xTop=xTop+size2

    for i in range(numbots):
        x, y = random.randint(0, 199), random.randint(0, 199)
        while [x, y] in botPose or not np.all(img[x, y] - [255, 255, 255] == 0):
            x, y = random.randint(0, 199), random.randint(0, 199)
        botPose.append([x, y])

    img[img.shape[0]-3:img.shape[0], img.shape[1]-3:img.shape[1]] = [0, 255, 0]
    greenZone.append([[img.shape[0]-3, img.shape[1]-3], [img.shape[0]-3, img.shape[1]-1], [img.shape[0]-1, img.shape[1]-1], [img.shape[0]-1, img.shape[1]-3]])

    # Shuffle the lists to prevent easy giveaways!
    random.shuffle(greenZone)
    random.shuffle(redZone)
    random.shuffle(obstaclePose)
    originalGreenZone = greenZone[:]

    im=Image.fromarray(img)
    im.save("images/map.png")
    return jsonify({'Map_Setup_Complete':True})

def check_mission(botId):
    global img, mission_complete, greenZone
    if np.all(img[botPose[botId][0], botPose[botId][1]] - np.array([255, 0, 0]), 0):
        move_score = 2
    else:
        move_score = 1
    for rect in greenZone:
        minx, miny = min([point[0] for point in rect]), min([point[1] for point in rect])
        maxx, maxy = max([point[0] for point in rect]), max([point[1] for point in rect])
        if minx <= botPose[botId][0] <= maxx and miny <= botPose[botId][1] <= maxy:
            greenZone = [r for r in greenZone if r != rect]
            img[rect[0][0]:rect[2][0]+1, rect[0][1]:rect[2][1]+1] = [0, 100, 0]
            break
    if len(greenZone) == 0:
        mission_complete = True
    return move_score


def check_and_move(botId, moveType):
    global img, botPose
    x = botPose[botId][0]
    y = botPose[botId][1]
    invalid_color = np.array([0,0,0])
    print(img[x,y])
    if moveType == 1:
        if x-1 >= 0 and  y-1 >= 0 and not np.all((img[x-1,y-1] - invalid_color) == 0) and not [x-1,y-1] in botPose:
            botPose[botId][0], botPose[botId][1] = x-1, y-1
            return True
    elif moveType == 2:
        if x-1 >= 0 and not np.all((img[x-1,y] - invalid_color) == 0) and not [x-1,y] in botPose:
            botPose[botId][0], botPose[botId][1] = x-1, y
            return True
    elif moveType == 3:
        if x-1 >= 0 and y+1 < img.shape[1] and not np.all((img[x-1,y+1] - invalid_color) == 0) and not [x-1,y+1] in botPose:
            botPose[botId][0], botPose[botId][1] = x-1, y+1
            return True
    elif moveType == 4:
        if y+1 < img.shape[1] and not np.all((img[x,y+1] - invalid_color) == 0) and not [x,y+1] in botPose:
            botPose[botId][0], botPose[botId][1] = x, y+1
            return True
    elif moveType == 5:
        if x+1 < img.shape[0] and y+1 < img.shape[1] and not np.all((img[x+1,y+1] - invalid_color) == 0) and not [x+1,y+1] in botPose:
            botPose[botId][0], botPose[botId][1] = x+1, y+1
            return True
    elif moveType == 6:
        if x+1 < img.shape[0] and not np.all((img[x+1,y] - invalid_color) == 0) and not [x+1,y] in botPose:
            botPose[botId][0], botPose[botId][1] = x+1, y
            return True
    elif moveType == 7:
        if x+1 < img.shape[0] and y-1 >= 0 and not np.all((img[x+1,y-1] - invalid_color) == 0) and not [x+1,y-1] in botPose:
            botPose[botId][0], botPose[botId][1] = x+1, y-1
            return True
    elif moveType == 8:
        if y-1 >= 0 and not np.all((img[x,y-1] - invalid_color) == 0) and not [x,y-1] in botPose:
            botPose[botId][0], botPose[botId][1] = x, y-1
            return True
    else:
        return False

# def setup():
#     global level, numbots
#     while level == 0:
#         level = int(input("Please enter level(1/2/3/4/5/6): "))
#         if not (0 < level < 7):
#             level = 0
#             continue
#         else:
#             # TODO: Guided tour of the level
#             if level == 1 or level == 2:
#                 numbots = 1
#             elif level == 3 or level == 5:
#                 numbots = 2
#             elif level == 4 or level == 6:
#                 numbots = min(8, int(input("Number of bots in play(max 8): ")))
#             else:
#                 level = 0
#                 continue


# def createImage(size1,size2):
#     global botPose, img, obstaclePose, greenZone, redZone, level, numbots, originalGreenZone
#     setup()

#     size=size2//2
#     arr=[[0,0],[0,1],[1,0],[1,1]]
#     random.seed(time.time())
#     img=np.ones((size1,size1,3),dtype=np.uint8)*255
#     xTop=0
#     while xTop<size1:
#         yTop=0
#         while yTop<size1:
#             num=random.randint(0,3)
#             newX=xTop+arr[num][0]*(size2//2)
#             newY=yTop+arr[num][1]*(size2//2)
#             if (newX==0 and newY==0) or (newX==size1-(size2//2) and newY==size1-(size2//2)):
#                 pass
#             else:
#                 # Single-objective environment
#                 if level == 1:
#                     img[newX:newX+(size2//2),newY:newY+(size2//2),:]=np.zeros((size2//2,size2//2,3))
#                     obstaclePose.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])

#                 # Multi-objective unconstrained environment
#                 elif level == 2 or level == 3 or level == 4:
#                     if np.random.random() < 0.3:
#                         img[newX:newX+(size2//2),newY:newY+(size2//2),:]=[0, 255, 0]
#                         greenZone.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
#                     else:
#                         img[newX:newX+(size2//2),newY:newY+(size2//2),:]=np.zeros((size2//2,size2//2,3))
#                         obstaclePose.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])

#                 # Multi-objective contrained environment
#                 else:
#                     srand = np.random.random()
#                     if srand < 0.3:
#                         img[newX:newX+(size2//2),newY:newY+(size2//2),:]=[0, 255, 0]
#                         greenZone.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
#                     elif srand < 0.5:
#                         img[newX:newX+(size2//2),newY:newY+(size2//2),:]=[255, 0, 0]
#                         redZone.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
#                     else:
#                         img[newX:newX+(size2//2),newY:newY+(size2//2),:]=np.zeros((size2//2,size2//2,3))
#                         obstaclePose.append([[newX,newY],[newX,newY+size-1],[newX+size-1,newY+size-1],[newX+size-1,newY]])
#             yTop=yTop+size2
#         xTop=xTop+size2

#     for i in range(numbots):
#         x, y = random.randint(0, 199), random.randint(0, 199)
#         while [x, y] in botPose or not np.all(img[x, y] - [255, 255, 255] == 0):
#             x, y = random.randint(0, 199), random.randint(0, 199)
#         botPose.append([x, y])

#     img[img.shape[0]-3:img.shape[0], img.shape[1]-3:img.shape[1]] = [0, 255, 0]
#     greenZone.append([[img.shape[0]-3, img.shape[1]-3], [img.shape[0]-3, img.shape[1]-1], [img.shape[0]-1, img.shape[1]-1], [img.shape[0]-1, img.shape[1]-3]])

#     # Shuffle the lists to prevent easy giveaways!
#     random.shuffle(greenZone)
#     random.shuffle(redZone)
#     random.shuffle(obstaclePose)
#     originalGreenZone = greenZone[:]

#     im=Image.fromarray(img)
#     im.save("images/map.png")

#createImage(200,40)

if  __name__=="__main__":
    app.run(debug = True)
