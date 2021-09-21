import requests
import time
from io import BytesIO
from PIL import Image
import numpy as np

'''
Feel free to visit explore each of the links after you have run setup.sh
'''

cmd_url = 'http://127.0.0.1:5000/move'
score_url = 'http://127.0.0.1:5000/score'
botPose_url = 'http://127.0.0.1:5000/botPose'
obstacle_url = 'http://127.0.0.1:5000/obstaclesPose'
greenZone_url =  'http://127.0.0.1:5000/greenZone'
original_greenZone_url = 'http://127.0.0.1:5000/originalGreenZone'
redZone_url = 'http://127.0.0.1:5000/redZone'
level_url = 'http://127.0.0.1:5000/level'
numbots_url = 'http://127.0.0.1:5000/numbots'
map_url='http://127.0.0.1:5000/map'
set_new_map_url='http://127.0.0.1:5000/set_new_map'


def send_command(botId, moveType):
    '''
    Inputs:
        botId       int     The ID of the bot
        moveType    int     movement type, as descriped in the README
    Returns:
        success             bool    True, if the move being tried happened, False otherwise
        mission_complete    bool    True, if all the goals have been completed

    Work:
        Use this command to instruct the zooid to move. If the zooid cannot move,
        because of obstacle, or another zooid already occupying the grid or all
        green regions have already been collected, then it will return False.
        Otherwise, it will update the position of the zooid with ID as botId to
        the required location and return True. Now, if all the green regions
        have been collected, the mission_complete value will be set to True
    '''
    command = {
                'botId': botId,
                'moveType':moveType,
    }
    r=requests.get(cmd_url,json=command)
    time.sleep(0.05)
    return r.json()['success'], r.json()['mission_complete']

def get_level():
    '''
    Inputs:

    Returns:
        level   int     The level which you're attempting
    '''
    r = requests.get(level_url)
    time.sleep(0.05)
    return r.json()['level']

def get_numbots():
    '''
    Inputs:

    Returns:
        numbots   int     Total number of zooids on the grid
    '''
    r = requests.get(numbots_url)
    time.sleep(0.05)
    return r.json()['numbots']

def get_score():
    '''
    Inputs:

    Returns:
        score   int     Total number of steps, the less the better
    '''
    r = requests.get(score_url)
    time.sleep(0.05)
    return r.json()['score']

def get_obstacles_list():
    '''
    Inputs:

    Returns:
        obs_list   list     Each element of the returned list is a list containing
                            4 vertices of the rectangular obstacle, in a
                            clockwise manner,starting from the left top corner
    Work:
    This represents the list of rectangular obstacles. You cannot move a zooid
    through an obstacle.
    '''
    r = requests.get(obstacle_url)
    time.sleep(0.05)
    return r.json()

def get_redZone_list():
    '''
    Inputs:

    Returns:
        red_list   list     Each element of the returned list is a list containing
                            4 vertices of the rectangular obstacle, in a
                            clockwise manner,starting from the left top corner
    Work:
    This represents the list of rectangular red regions. You can move a zooid
    through a red region, but you have to pay twice the number of steps. So try
    and avoid this region, unless the other viable path is really long.
    '''
    r = requests.get(redZone_url)
    time.sleep(0.05)
    return r.json()

def get_greenZone_list():
    '''
    Inputs:

    Returns:
        green_list   list   Each element of the returned list is a list containing
                            4 vertices of the rectangular obstacle, in a
                            clockwise manner,starting from the left top corner
    Work:
    This represents the list of rectangular green regions. Each green region must
    be visited by at least one zooid, and a green region is said to be visited,
    if any zooid passes through at least one of its grid.

    Please keep in mind, that this is a dynamic list. That is, once a green region
    is visited, it is moved out of this list. So the mission is to get this list empty.
    '''
    r = requests.get(greenZone_url)
    time.sleep(0.05)
    return r.json()

def get_original_greenZone_list():
    '''
    Inputs:

    Returns:
        green_list   list   Each element of the returned list is a list containing
                            4 vertices of the rectangular obstacle, in a
                            clockwise manner,starting from the left top corner
    Work:
    Same as the list of green regions, except that, this list is not changed. So,
    it would contain all the green regions that were there in the beginning
    '''
    r = requests.get(original_greenZone_url)
    time.sleep(0.05)
    return r.json()


def get_botPose_list():
    '''
    Inputs:

    Returns:
        botPose     list    Each element of the returned list is a list containing
                            2 elements (x, y) denoting the position of the zooids
                            on the grid.
    Work:
    Contains the updated list of position of the zooids on the grid. This is the
    most important function, in terms of feedback.
    '''
    r = requests.get(botPose_url)
    time.sleep(0.05)
    return r.json()

def get_Map():
    '''
    Inputs:

    Returns:
        numpy array of map image
    Work:
    '''
    r = requests.get(map_url)
    img = np.array(Image.open(BytesIO(r.content)))
    return img

def set_new_map(level, numbots):
    '''
    Inputs:

    Returns:
        Truth value of reset success
    Work:
        Resets Map before a retry
    '''
    command = {
                'level': level, 'numbots':numbots
    }
    r = requests.get(set_new_map_url, json=command)
    time.sleep(0.05)
    return r.json
