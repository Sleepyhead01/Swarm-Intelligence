'''
DEPENDENCIES:

Numpy
Travelling Salesman solution library: pip3 install python-tsp
Scikit-learn: pip3 install -U scikit-learn
'''

from os import pathconf_names
import sys

from numpy.core.records import array
from api import *
from time import process_time, sleep
import numpy as np
import random as r
from math import inf, sqrt

from python_tsp.exact import solve_tsp_dynamic_programming

from sklearn.cluster import KMeans


#######    YOUR CODE FROM HERE #######################
import random
grid =[]
neigh=[[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1]]

class Node:
	def __init__(self,value,point):
		self.value = value  #0 for blocked,1 for unblocked, 2 for redzone
		self.point = point
		self.parent = None
		self.move=None
		self.H = 0
		self.G = 0
		
def isValid(pt):
	return pt[0]>=0 and pt[1]>=0 and pt[0]<200 and pt[1]<200

def neighbours(point):  #returns valid neighbours
	global grid,neigh
	x,y = point.point
	links=[]
	for i in range(len(neigh)):
		newX=x+neigh[i][0]
		newY=y+neigh[i][1]
		if not isValid((newX,newY)):
			continue
		links.append((i+1,grid[newX][newY]))
	return links

# returns the distance b/w two nodes(Heuristic for A*)
def diagonal(point,point2):
	return sqrt((point.point[0]-point2.point[0])**2 + (point.point[1]-point2.point[1])**2)

def aStar(start, goal):
	#declaring empty open and closed lists
	openList = set()
	closedList = set()
	#Current point is the starting point
	current = start
	#adding current node to open list
	openList.add(current)
	#While the open set is not empty
	while openList:
		#consider the node with the lowest f(=g+h) score in the open list
		current = min(openList, key=lambda o:o.G + o.H)
		#Remove the item from the open set
		openList.remove(current)
		#Add it to the closed set
		closedList.add(current)
		#if (this node is our destination node) we are done
		if current == goal:
			path = []
			while current.parent:
				path.append(current)
				current = current.parent                
				if(current.point==start.point):
					path.append(current)
					return path[::-1], goal.G
		#if not put the current node in the closed list and look at all of its neighbors 
		for move,node in neighbours(current):
			#If it is already in the closed set, skip it
			if node in closedList:
				continue
			#if cell is blocked
			if node.value==0:
				continue
			#Otherwise if it is already in the open set
			if node in openList:
				#the product of the difference of diagoal neighbours and current bot position is -1 or 1
				# this is used to update the scores of diagonal neighbours(1.414) 
				parity = (current.point[0] - node.point[0])*(current.point[1] - node.point[1])
				#Check G score 
				if node.value == 1:
					gUpdate = current.G  + diagonal(node, current)
					if parity is 1 or -1:
						gUpdate += 0.414
				elif node.value == 2:
					gUpdate = current.G + 2*diagonal(node, current)
					# if parity is 1 or -1:
					# 	gUpdate += 0.414 
				if node.G > gUpdate:
					#If so, update the node to have a new parent
					node.G = gUpdate
					node.parent = current
					node.move=move
			else:
				#If it isn't in the open set, calculate the G and H score for the node
				parity = (current.point[0] - node.point[0])*(current.point[1] - node.point[1])
				if node.value == 1:
					gUpdate = current.G + diagonal(node, current) 
					if parity is 1 or -1:
						gUpdate += 0.414
				elif node.value == 2:
					gUpdate = current.G + 2*diagonal(node, current)
					# if parity is 1 or -1:
					# 	gUpdate += 0.414 
				node.H = diagonal(node, goal)
				#Set the parent to our current item
				node.G = gUpdate

				node.parent = current
				node.move=move
				#Add it to the set
				openList.add(node)

#this function converts the 200x200 pixel into a graph taking into account the blocked/open/red zones
def makeGrid():
	obstaclePose = get_obstacles_list()
	redZone = get_redZone_list()
	
	for i in range(200):
		grid.append([])
		for j in range(200):
			grid[i].append(Node(1,(i,j)))
	for pt in obstaclePose:
		for i in range(pt[0][0],pt[2][0]+1):
			for j in range(pt[0][1],pt[2][1]+1):
				grid[i][j]=Node(0,(i,j))
	for pt in redZone:
		for i in range(pt[0][0],pt[2][0]+1):
			for j in range(pt[0][1],pt[2][1]+1):
				grid[i][j]=Node(2,(i,j))
	
'''########## Level 1 ##########'''
def level1(botId):
	global grid
	greenZone = get_greenZone_list()

	#constructing the graph	
	makeGrid()

	botsPose = get_botPose_list()

	#initial bot position is start
	start=grid[botsPose[0][0]][botsPose[0][1]]
	
	goal=grid[greenZone[0][0][0]][greenZone[0][0][1]]

	#calling aStar and storing path
	path, _ = aStar(start, goal)
	
	#moving the bot
	for i in range(1,len(path)):
		successful_move, mission_complete = send_command(botId,path[i].move)
	

'''
In this level, my solution is inspired by the Travelling Salesman Problem(TSP). 
The Green Zones are considered as 'cities'(nodes) and the distance
b/w them as the weight of edge. Ofcourse the bot is the salesman.
NOTE: Please install the Travelling Salesman solution library using pip3 install python-tsp
Although I tried to implement TSP on my own, it was not fast enough, due to my limited
coding knowledge.(Also, the complexity O(n!)) Hence, I used an open sourced library that uses 
dynamic programming to compute TSP.
'''

'''########## Level 2 ##########'''
def level2(botId):
	global grid
	botsPose = get_botPose_list()
	greenZone = get_greenZone_list()

	makeGrid()

	# No. of green Zones
	nGreenZone = len(greenZone)
	
	'''
	Declaring the adjecency matrix for solving TSP as a graph.
	The entry (i,j) in the scoreMatrix represents the 'cost' to travel from i'th position 
	to j'th position.
	'''
	matrixLen = nGreenZone + 1
	scoreMatrix = [0]*(matrixLen*matrixLen)

	#initial position os bot
	start=grid[botsPose[0][0]][botsPose[0][1]]

	'''
	The two loops below compute the A* heuristic score which is used as the 
	weight of edges b/w two (nodes)greenZones.
	Although it takes about a minute to compute, th overall result is better.
	'''
	# print("Computing A* costs. \n It might feel like the script froze but it hasn't. \n It takes some time to compute TSP for many Green Zones. Please wait!")
	# for i in range(1, matrixLen):
	# 	goal=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
	# 	path, score =aStar(start, goal)
	# 	scoreMatrix[i*matrixLen] = score
	# 	scoreMatrix[i] = scoreMatrix[i*matrixLen]


	# for i in range(1, matrixLen):
	# 	for j in range(1, matrixLen):
	# 		if i == j :
	# 			continue
	# 		start=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
	# 		goal=grid[greenZone[j-1][0][0]][greenZone[j-1][0][1]]
	# 		path, score =aStar(start, goal)
	# 		scoreMatrix[i*matrixLen +j] = score
	
	'''
	My 2nd approach, using the Euclidean distance as the weight of the edges.
	It is worthwhile to note that, although the obstacles are disregarded completely
	in this approach, the results are quite similar to the A* heuristic approach. 
	Also this approach is computationaly more efficient than the previous approach.
	PLEASE COMMENT THE ABOVE TWO LOOPS AND UNCOMMENT THE BELOW TWO, TO USE THIS APPROACH.
	'''

	for i in range(1, matrixLen):
		goal=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
		score = diagonal(start, goal)
		scoreMatrix[i*matrixLen] = score
		scoreMatrix[i] = scoreMatrix[i*matrixLen]


	for i in range(1, matrixLen):
		for j in range(1, matrixLen):
			if i == j :
				continue
			start=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
			goal=grid[greenZone[j-1][0][0]][greenZone[j-1][0][1]]
			score = diagonal(start, goal)
			scoreMatrix[i*matrixLen +j] = score

	scoreMatrix = np.reshape(scoreMatrix, (matrixLen, matrixLen))	
	botTaskSeq, _ = solve_tsp_dynamic_programming(scoreMatrix)

	# -1 bkz Green Zone index starts at 0 and doesn't contain bot's initial position
	m = botTaskSeq[1] - 1

	# moving the bot
	start=grid[botsPose[0][0]][botsPose[0][1]]
	goal=grid[greenZone[m][0][0]][greenZone[m][0][1]]
	path, score = aStar(start, goal)
	for i in range(1,len(path)):
		successful_move, mission_complete = send_command(botId,path[i].move)

	for j in range(1, matrixLen-1):
		m = botTaskSeq[j]-1
		o = botTaskSeq[j+1]-1
		start=grid[greenZone[m][0][0]][greenZone[m][0][1]]
		goal=grid[greenZone[o][0][0]][greenZone[o][0][1]]
		path, score = aStar(start, goal)
		for i in range(1,len(path)):
			successful_move, mission_complete = send_command(botId,path[i].move)

'''
The funtions below are relevant for levels 3 - 6
'''
#returns euclidean distance b/w two points
def dist(p1, p2):
	return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)	

#returns the centre of green zone 
def centreGreenZone(greenZone):
	centreGreenZone = []
	for i in range(len(greenZone)):
		centreGreenZone.append((np.sum(greenZone[i], axis=0)/4))
	return centreGreenZone

#clusters the greenZones according to proximity(using K-means clustering)
#inputs: number of clusters required
def create_clusters(number_of_clusters,points):
    kmeans = KMeans(n_clusters=number_of_clusters, random_state=0).fit(points)
    l_array = np.array([[label] for label in kmeans.labels_])
    clusters = np.append(points,l_array,axis=1)
    return clusters, kmeans.cluster_centers_

'''
For, levels 3 - 6, a general optimal algorithm could not be implemented by me. Therefore,
these levels were handled on a case basis. 
Case 1: No. of bots(=n) < No. of Green Zones:
		Green zones were divided into 'n' clusters according to proximity. The bot closest to the
		centre of the cluster was chosen to visit the green zones in that particular cluster.
Case 2: No. of bots >= No. of Green Zones(=m): 
		'm' bots were chosen and each was assigned a greenzone closest to it.
'''

'''
LIMITATIONS AND FUTURE WORK:
1. In general some of these levels don't have optimal solutions, so, it can't be modelled mathematically.
   Therefore, Genetic Algorithm or RL Agents can be used to capture such higher level abstractions.
   The key challenge is to partion the tasks and choose the number of bots to be used, after which
   TSP and A* can be used to find the optimal path and sequence of green zone traversal.
2. Although the above heuristic was efficient in most cases, the solution would be better if the 
   clustering of green zones was done taking into account the relative positions of the bots(such that 
   they don't cross over) and that there was a tradeoff b/w the no. of bots used and the no. of clusters.
   (Instead the no. of clusters was enforced by the number of bots, which is illogical in some typical
   cases. For eg. If no. of green zones = 6(of which 5 are very close), and no. of bots = 5, 2 bots would
   suffice. Instead, Case 2 of policyPicker is used which unnecessaryly uses all the 5 bots)
'''
def policyPicker(greenZone, botsPose, numBots, botId):
	nGreenZone = len(greenZone)

	#Case 2:No. of bots >= No. of Green Zones
	if (nGreenZone <= numBots):
		botClusterDist = np.zeros((numBots,numBots))

		# Distance b/w bots and green zones
		for i in range (numBots):
			for j in range (nGreenZone):
				botClusterDist[i,j] = dist(botsPose[i],greenZone[j][0])

		botFilter = np.arange(numBots)	#checklist for bots
		zoneFilter = np.arange(nGreenZone)	#checklist for greenzones
		botAssign = []	#stores the inesx of assigned bot & greenzone
		while len(zoneFilter) > 0:	#assigning bots to greenzones
			minDist = botClusterDist.min()
			botSelect = np.where(botClusterDist == minDist)
			if (botSelect[0] in botFilter) and (botSelect[1] in zoneFilter) :
				botAssign.append(botSelect)
				botFilter = botFilter[botFilter!= botSelect[0]]
				zoneFilter = zoneFilter[zoneFilter!= botSelect[1]]
			botClusterDist[botSelect[0],botSelect[1]] = inf

		botAssign =  (np.squeeze((np.array(botAssign)).tolist())).tolist()
		botAssign.sort()

		# moving the bot acc to botId
		for i in range(len(botAssign)):
				if botId == (botAssign[:][i][0]):
					botTask = botAssign[i][1]
					start=grid[botsPose[botId][0]][botsPose[botId][1]]
					goal=grid[greenZone[botTask][0][0]][greenZone[botTask][0][1]]

					path, _ = aStar(start, goal)
					
					for i in range(1,len(path)):
						successful_move, mission_complete = send_command(botId,path[i].move)


	else:
		# Case 1: No. of bots(=n) < No. of Green Zones
		
		greenZoneCor = (np.array(greenZone))[:,0]
		#Clustering
		cluster, clusterCentre = create_clusters(numBots,greenZoneCor)
		
		enumerate = np.arange(nGreenZone)
		enumerate = np.reshape(enumerate,(1,nGreenZone))
		cluster = np.hstack([cluster, enumerate.T])
		cluster = cluster[cluster[:,2].argsort()]
		cluster = cluster[:,2:4]
		individualTask = (np.split(cluster, np.where(np.diff(cluster[:,0]))[0]+1))	# sorted clusters
		
		#assigning bots to clusters(similar to case 2 above)
		botClusterDist = np.zeros((numBots,numBots))

		for i in range (numBots):
			for j in range (numBots):
				botClusterDist[i,j] = dist(botsPose[i],clusterCentre[j])

		botFilter = np.arange(numBots)
		zoneFilter = np.arange(nGreenZone)
		botAssign = []
		while len(botFilter) > 0:
			minDist = botClusterDist.min()
			botSelect = np.where(botClusterDist == minDist)
			if (botSelect[0] in botFilter) and (botSelect[1] in zoneFilter) :
				botAssign.append(botSelect)
				botFilter = botFilter[botFilter!= botSelect[0]]
				zoneFilter = zoneFilter[zoneFilter!= botSelect[1]]
			botClusterDist[botSelect[0],botSelect[1]] = inf

		#finding the best path for the current bot using TSP
		currentBot = int(botAssign[botId][0])
		currentTask = int(botAssign[botId][1])
		botTask = individualTask[currentTask][:,1]
		matrixLen = len(botTask) + 1
		scoreMatrix = [0]*(matrixLen*matrixLen)
		start=grid[botsPose[currentBot][0]][botsPose[currentBot][1]]
		greenZone1 = []
		for i in range(0, matrixLen -1):
			greenZone1.append(greenZone[botTask[i]])

		for i in range(1, matrixLen):
			goal=grid[greenZone1[i-1][0][0]][greenZone1[i-1][0][1]]
			_, score = aStar(start, goal)

			scoreMatrix[i*matrixLen] = score
			scoreMatrix[i] = scoreMatrix[i*matrixLen]


		for i in range(1, matrixLen):
			for j in range(1, matrixLen):
				if i == j :
					continue
				start=grid[greenZone1[i-1][0][0]][greenZone1[i-1][0][1]]
				goal=grid[greenZone1[j-1][0][0]][greenZone1[j-1][0][1]]
				_, score = aStar(start, goal)

				scoreMatrix[i*matrixLen +j] = score

		scoreMatrix = np.reshape(scoreMatrix, (matrixLen, matrixLen))	

		permutation, _ = solve_tsp_dynamic_programming(scoreMatrix)
		m = permutation[1] - 1
		start=grid[botsPose[currentBot][0]][botsPose[currentBot][1]]
		goal=grid[greenZone1[m][0][0]][greenZone1[m][0][1]]
		path, score = aStar(start, goal)
		
		#moving the bot
		for i in range(1,len(path)):
			successful_move, mission_complete = send_command(currentBot,path[i].move)

		for j in range(1, matrixLen-1):
			m = permutation[j]-1
			o = permutation[j+1]-1
			start=grid[greenZone1[m][0][0]][greenZone1[m][0][1]]
			goal=grid[greenZone1[o][0][0]][greenZone1[o][0][1]]
			path, score = aStar(start, goal)
			for i in range(1,len(path)):
				successful_move, mission_complete = send_command(currentBot,path[i].move)


'''########## Level 3 ##########'''
def level3(botId):
	global grid

	numBots = get_numbots()
	botsPose = get_botPose_list()
	greenZone = get_original_greenZone_list()
	
	makeGrid()

	#1st Approach
	policyPicker(greenZone, botsPose, numBots, botId)
	
	'''
	2nd Approach: Tracking the bot's dynammic position as after it completes each green zone to allocate
	best possible next green zone. 
	NOTE: Comment out 'policyPicker(greenZone, botsPose, numBots, botId)' and uncomment the below 
	code for 2nd approach.
	'''	
	# # No. of green Zones
	# nGreenZone = len(greenZone)

	# centreOfGreenZone = []
	# centreOfGreenZone = centreGreenZone(greenZone)

	# individualTask1 = []
	# individualTask2 = []
	# avgBotPose = [botsPose[0], botsPose[1]]
	

	# for i in range(nGreenZone):
	# 	if dist(centreOfGreenZone[i], avgBotPose[0]) < dist(centreOfGreenZone[i], avgBotPose[1]):
	# 		avgBotPose[0] = [(avgBotPose[0][0]+centreOfGreenZone[i][0])/2,(avgBotPose[0][1]+centreOfGreenZone[i][1])/2]
	# 		individualTask1.append(i)
	# 	else:
	# 		avgBotPose[1] = [(avgBotPose[1][0]+centreOfGreenZone[i][0])/2,(avgBotPose[1][1]+centreOfGreenZone[i][1])/2]
	# 		individualTask2.append(i)

	# individualTask = [individualTask1] + [individualTask2]
	
	# matrixLen = len(individualTask[botId]) + 1
	# scoreMatrix = [0]*(matrixLen*matrixLen)

	# greenZone1 = []
	# for i in range(0, matrixLen -1):
	# 	greenZone1.append(greenZone[individualTask[botId][i]])

	# start=grid[botsPose[botId][0]][botsPose[botId][1]]

	# '''
	# A* cost adjecency matrix approach
	# '''
	# for i in range(1, matrixLen):
	# 	goal=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
	# 	path, score = aStar(start, goal)
	# 	scoreMatrix[i*matrixLen] = score
	# 	scoreMatrix[i] = scoreMatrix[i*matrixLen]


	# for i in range(1, matrixLen):
	# 	for j in range(1, matrixLen):
	# 		if i == j :
	# 			continue
	# 		start=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
	# 		goal=grid[greenZone[j-1][0][0]][greenZone[j-1][0][1]]
	# 		path, score = aStar(start, goal)
	# 		scoreMatrix[i*matrixLen +j] = score

	# '''
	# Euclidean distance approach
	# '''
	# # for i in range(1, matrixLen):
	# # 	goal=grid[greenZone1[i-1][0][0]][greenZone1[i-1][0][1]]
	# # 	score = diagonal(start, goal)
	# # 	scoreMatrix[i*matrixLen] = score
	# # 	scoreMatrix[i] = scoreMatrix[i*matrixLen]

	# # for i in range(1, matrixLen):
	# # 	for j in range(1, matrixLen):
	# # 		if i == j :
	# # 			continue
	# # 		start=grid[greenZone1[i-1][0][0]][greenZone1[i-1][0][1]]
	# # 		goal=grid[greenZone1[j-1][0][0]][greenZone1[j-1][0][1]]
	# # 		score = diagonal(start, goal)
	# # 		scoreMatrix[i*matrixLen +j] = score

	# scoreMatrix = np.reshape(scoreMatrix, (matrixLen, matrixLen))	

	# permutation, distance = solve_tsp_dynamic_programming(scoreMatrix)

	# m = permutation[1]-1
	# start=grid[botsPose[botId][0]][botsPose[botId][1]]
	# goal=grid[greenZone1[m][0][0]][greenZone1[m][0][1]]
	# path, score = aStar(start, goal)
	# for i in range(1,len(path)):
	# 		successful_move, mission_complete = send_command(botId,path[i].move)

	# for j in range(1, matrixLen-1):
	# 	m = permutation[j]-1
	# 	o = permutation[j+1]-1
	# 	start=grid[greenZone1[m][0][0]][greenZone1[m][0][1]]
	# 	goal=grid[greenZone1[o][0][0]][greenZone1[o][0][1]]
	# 	path, score = aStar(start, goal)
	# 	for i in range(1,len(path)):
	# 		successful_move, mission_complete = send_command(botId,path[i].move)



'''########## Level 4 ##########'''
def level4(botId):
	global grid

	numBots = get_numbots()
	botsPose = get_botPose_list()
	greenZone = get_original_greenZone_list()

	makeGrid()
	policyPicker(greenZone, botsPose, numBots, botId)
	

'''########## Level 5 ##########'''

def level5(botId):
	global grid
	botsPose = get_botPose_list()
	greenZone = get_original_greenZone_list()

	numBots = get_numbots()

	makeGrid()
	policyPicker(greenZone, botsPose, numBots, botId)
	
	'''
	NOTE: Comment out 'policyPicker(greenZone, botsPose, numBots, botId)' and uncomment the below 
	code for 2nd approach.
	'''	
	# nGreenZone = len(greenZone)

	# centreOfGreenZone = []
	# centreOfGreenZone = centreGreenZone(greenZone)

	# individualTask1 = []
	# individualTask2 = []
	# avgBotPose = [botsPose[0], botsPose[1]]
	

	# for i in range(nGreenZone):
	# 	if dist(centreOfGreenZone[i], avgBotPose[0]) < dist(centreOfGreenZone[i], avgBotPose[1]):
	# 		avgBotPose[0] = [(avgBotPose[0][0]+centreOfGreenZone[i][0])/2,(avgBotPose[0][1]+centreOfGreenZone[i][1])/2]
	# 		individualTask1.append(i)
	# 	else:
	# 		avgBotPose[1] = [(avgBotPose[1][0]+centreOfGreenZone[i][0])/2,(avgBotPose[1][1]+centreOfGreenZone[i][1])/2]
	# 		individualTask2.append(i)

	# individualTask = [individualTask1] + [individualTask2]
	
	# matrixLen = len(individualTask[botId]) + 1
	# scoreMatrix = [0]*(matrixLen*matrixLen)

	# greenZone1 = []
	# for i in range(0, matrixLen -1):
	# 	greenZone1.append(greenZone[individualTask[botId][i]])

	# start=grid[botsPose[botId][0]][botsPose[botId][1]]

	# '''
	# A* cost adjecency matrix approach
	# '''
	# for i in range(1, matrixLen):
	# 	goal=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
	# 	path, score = aStar(start, goal)
	# 	scoreMatrix[i*matrixLen] = score
	# 	scoreMatrix[i] = scoreMatrix[i*matrixLen]


	# for i in range(1, matrixLen):
	# 	for j in range(1, matrixLen):
	# 		if i == j :
	# 			continue
	# 		start=grid[greenZone[i-1][0][0]][greenZone[i-1][0][1]]
	# 		goal=grid[greenZone[j-1][0][0]][greenZone[j-1][0][1]]
	# 		path, score = aStar(start, goal)
	# 		scoreMatrix[i*matrixLen +j] = score

	# '''
	# Euclidean distance approach
	# '''
	# # for i in range(1, matrixLen):
	# # 	goal=grid[greenZone1[i-1][0][0]][greenZone1[i-1][0][1]]
	# # 	score = diagonal(start, goal)
	# # 	scoreMatrix[i*matrixLen] = score
	# # 	scoreMatrix[i] = scoreMatrix[i*matrixLen]

	# # for i in range(1, matrixLen):
	# # 	for j in range(1, matrixLen):
	# # 		if i == j :
	# # 			continue
	# # 		start=grid[greenZone1[i-1][0][0]][greenZone1[i-1][0][1]]
	# # 		goal=grid[greenZone1[j-1][0][0]][greenZone1[j-1][0][1]]
	# # 		score = diagonal(start, goal)
	# # 		scoreMatrix[i*matrixLen +j] = score

	# scoreMatrix = np.reshape(scoreMatrix, (matrixLen, matrixLen))	

	# permutation, distance = solve_tsp_dynamic_programming(scoreMatrix)

	# m = permutation[1]-1
	# start=grid[botsPose[botId][0]][botsPose[botId][1]]
	# goal=grid[greenZone1[m][0][0]][greenZone1[m][0][1]]
	# path, score = aStar(start, goal)
	# for i in range(1,len(path)):
	# 		successful_move, mission_complete = send_command(botId,path[i].move)

	# for j in range(1, matrixLen-1):
	# 	m = permutation[j]-1
	# 	o = permutation[j+1]-1
	# 	start=grid[greenZone1[m][0][0]][greenZone1[m][0][1]]
	# 	goal=grid[greenZone1[o][0][0]][greenZone1[o][0][1]]
	# 	path, score = aStar(start, goal)
	# 	for i in range(1,len(path)):
	# 		successful_move, mission_complete = send_command(botId,path[i].move)
	

'''########## Level 6 ##########'''
def level6(botId):    
	global grid

	numBots = get_numbots()
	botsPose = get_botPose_list()
	greenZone = get_original_greenZone_list()

	
	makeGrid()

	nGreenZone = len(greenZone)
	policyPicker(greenZone, botsPose, numBots, botId)



#######    DON'T EDIT ANYTHING BELOW  #######################

if  __name__=="__main__":
	botId = int(sys.argv[1])
	level = get_level()
	if level == 1:
		level1(botId)
	elif level == 2:
		level2(botId)
	elif level == 3:
		level3(botId)
	elif level == 4:
		level4(botId)
	elif level == 5:
		level5(botId)
	elif level == 6:
		level6(botId)
	else:
		print("Wrong level! Please restart and select correct level")

