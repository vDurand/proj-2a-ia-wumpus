# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

# @file wumpusworld.py
#
# @author Régis Clouard
#
# Definition of the wumpus world
# and its visual rendering.

import Tkinter
from math import *
import random
import time

from utils import *

class WumpusFrame( Tkinter.Frame ):
    """
    This is the class for the window displaying the wumpus and its world.
    """
    __cellSize = 50

    def __init__( self, gridSize, simulationSpeed, agent ):
        """
        Creates the visual rendering of the wumpus world.
        """
        Tkinter.Frame.__init__(self,None)
        self.simulationSpeed = simulationSpeed
        self.master.title('Wumpus World')
        self.canvas = Tkinter.Canvas(self,
                                     width = self.__cellSize * gridSize,
                                     height = self.__cellSize * gridSize + 20,
                                     bg = 'white')
        self.gridSize = gridSize
        self.canvas.pack(expand = 1, anchor = Tkinter.CENTER)
        self.pack()
        self.tkraise()
        
        # Create the world
        self.tw = WumpusWorld(gridSize, agent)

        # Read the images
        self.images = {}
        for imageName in ['wall', 'ground', 'wumpus', 'dead-wumpus', 'gold', 'pit',
                    'agentup','agentdown','agentright','agentleft']:
            self.images[imageName] = Tkinter.PhotoImage(file = './images/' + imageName + '.gif')

        self.agentSprite = AgentSprite(self.__cellSize, self.images)
        self.projectile = ArrowSprite(self.__cellSize)

        # Display the empty world    
        for y in range(gridSize):
            for x in range(gridSize):
                self.canvas.create_image(x * self.__cellSize,
                                         y * self.__cellSize,
                                         image = self.images['ground'],
                                         anchor = Tkinter.NW)
                if self.tw.worldmap[y][x] != 'ground':
                    self.canvas.create_image(x * self.__cellSize, y * self.__cellSize,
                                             image = self.images[self.tw.worldmap[y][x]],
                                             anchor = Tkinter.NW)

        # Set up text item for drawing info
        self.textItem = self.canvas.create_text(0,
                                                (gridSize) * self.__cellSize,
                                                anchor = Tkinter.NW,
                                                text = '')
        self.after(1, self.step)

    def step( self ):
        """
        Manages the game cycle.
        """
        # Update current time
        self.tw.currentTime += 0.1

        # Move the agent 
        if self.tw.currentTime >= self.tw.nextWumpusTime:
            self.tw.stepAgent()
            # Update ground if necessary
            if self.tw.updateCurrentPlace:
                self.canvas.create_image(self.tw.xpos * self.__cellSize,
                                         self.tw.ypos * self.__cellSize,
                                         image = self.images[self.tw.worldmap[self.tw.ypos][self.tw.xpos]],
                                         anchor = Tkinter.NW)
            if self.tw.updatePlace:
                self.canvas.create_image(self.tw.updatePlace[0] * self.__cellSize,
                                         self.tw.updatePlace[1] * self.__cellSize,
                                         image = self.images['ground'],
                                         anchor = Tkinter.NW)
                self.canvas.create_image(self.tw.updatePlace[0] * self.__cellSize,
                                         self.tw.updatePlace[1] * self.__cellSize,
                                         image = self.images[self.tw.worldmap[self.tw.updatePlace[1]][self.tw.updatePlace[0]]],
                                         anchor = Tkinter.NW)
            if self.tw.action == 'forward':
                self.agentSprite.move(self.tw.direction, self.tw.xpos, self.tw.ypos, self.canvas)
            elif self.tw.action == 'shoot':
                self.projectile.launcharrow(self.tw.direction, self.tw.xpos, self.tw.ypos, self.canvas)
            else:
                self.agentSprite.display(self.tw.direction, self.tw.xpos, self.tw.ypos, self.canvas)
                
        # Display text information
        self.canvas.itemconfigure(self.textItem, 
                                  text = 'Score: %5d Projectile: %1d  Action: %-7s' % (self.tw.score, self.tw.arrowinventory, self.tw.action))

        if self.tw.action == 'dead':
            self.gameOver()
            self.end_graphics()
            return 0
        elif self.tw.action == 'end':
            self.gameWin()
            self.end_graphics()
            return 1
    
        elif self.tw.currentTime > self.tw.MAX_TIME:
            self.gameOver()
            return 0
        else:
            self.after(int(200 / self.simulationSpeed), self.step)
            return 0

   #game is over function looks at self to determine if game has reached the wumpus
    #indicates game has been won and prints out the game over gif to indicate the game has been lost
    def gameOver( self ):
        gameover = Tkinter.PhotoImage(file = 'images/gameover.gif')
        self.canvas.create_image((self.gridSize * self.__cellSize - 277) / 2,
                                 (self.gridSize * self.__cellSize - 73) / 2,
                                 image = gameover,
                                 anchor = Tkinter.NW)
        self.canvas.update_idletasks()
        time.sleep(3)

    #game is won and it prints out if the 
    def gameWin( self ):
        gamewin = Tkinter.PhotoImage(file = 'images/winner.gif')
        self.canvas.create_image((self.gridSize * self.__cellSize - 208) / 2,
                                 (self.gridSize * self.__cellSize - 76) / 2,
                                 image = gamewin,
                                 anchor = Tkinter.NW)
        self.canvas.update_idletasks()
        time.sleep(3)

    def end_graphics( self ):
        try:
            self.master.destroy()
        except SystemExit, e:
            print 'Ending graphics raised an exception:', e

class WumpusWorld():
    """
    The wumpus world as a map of cells.
    Manages the game cycle: moves both the agent
    according to the think() result.
    """
    MAX_TIME = 5000
    xpos, ypos = 1, 1
    currentTime = 0.0
    direction = 1 #north=0, east=1, south=2, west=3
    worldmap = None
    action = 'None'
    nextWumpusTime = 0
    updateCurrentPlace = False
    score = 0
    __wumpusCount = 0
    __goldCount = 0
    __bump = False
    __scream = False
    arrowinventory = 1

    def __init__( self, gridSize, wumpusAgent ):
        self.directionTable = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
        self.createWorldMap(gridSize)
        self.gridSize = gridSize
        self.wumpusAgent = wumpusAgent

    def createWorldMap( self, gridSize ):
        """
        Builds a random world map with pits, gold and wumpus.
        """
        self.worldmap = [[((y in [0, gridSize - 1] or  x in [0, gridSize - 1]) and 'wall') or 'ground'
                          for x in range(gridSize)] for y in range(gridSize)]
        # First put out the pits randomly
        for i in range(int(((gridSize - 2) ** 2) * 0.1)):
            ok = False
            while not ok: 
                (x, y) = random.randint(1, gridSize  -1), random.randint(1, gridSize - 1)
                if self.worldmap[y][x] == 'ground' and (x != 1 or y != 1):
                    pitCount = 0
                    wallCount = 0
                    # Check that the pits will not be adjacent to two other pits,
                    # or one other pit and a wall.
                    # This is to prevent the appearance of inaccessible areas.
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                           if self.worldmap[y+dy][x+dx] == 'pit':
                               pitCount += 1
                           if self.worldmap[y+dy][x+dx] == 'wall':
                               wallCount += 1
                    if pitCount == 0 or (pitCount <= 1 and wallCount == 0):        
                        self.worldmap[y][x] = 'pit'
                        ok = True
                    elif random.random() <= 0.1:
                        ok  = True

        # Then put out the gold randomly
        ok = False
        while not ok: 
            (x, y) = random.randint(1,gridSize-1), random.randint(1,gridSize-1)
            if self.worldmap[y][x] == 'ground' and (x != 1 or y != 1):
                self.worldmap[y][x] = 'gold'
                ok = True

        # Finally put out the wumpus randomly
        ok = False
        while not ok: 
            (x,y) = random.randint(1, gridSize - 1), random.randint(1, gridSize - 1)
            if self.worldmap[y][x] == 'ground'  and (x != 1 or y != 1):
                self.worldmap[y][x] = 'wumpus'
                self.__wumpusCount += 1
                ok = True

    def stepAgent( self ):
        """
        Moves the agent one step forward.
        """
        self.nextWumpusTime += 10
        self.updateCurrentPlace = False
        dx, dy = self.directionTable[self.direction]

        ahead = self.worldmap[self.ypos + dy][self.xpos + dx]
        here = self.worldmap[self.ypos][self.xpos]

        if here == 'pit' or here == 'wumpus':
            self.action = "dead"
            self.score -= 1000
            return

        stench = (here == 'dead-wumpus')
        breeze = False
        glitter = (here == 'gold')
        for k,l in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
            square = self.worldmap[self.ypos + k][self.xpos + l]
            if square == 'wumpus' or square == 'dead-wumpus':
                stench = True
            elif square == 'pit':
                breeze = True

        # Agent thinks (no more than 1s)!
        timed_func = TimeoutFunction(self.wumpusAgent.think, 1000)
        try:
            start_time = time.time()
            percept = Percept(stench, breeze, glitter, self.__bump, self.__scream)
            self.action = timed_func(percept)
        except TimeoutFunctionException:
            print "Timed out on a single move!"

        if self.action == 'end':
            return

        # Perform action
        self.__scream = False
        self.updatePlace = None
        if self.action == 'left':
            self.direction = (self.direction - 1) % 4
            self.score -= 1

        elif self.action == 'right':
            self.direction = (self.direction + 1)  %4
            self.score -= 1

        elif self.action == 'forward':
            if ahead == 'wall':
                self.__bump = True
                self.action = 'wait'
            else:
                self.xpos += dx
                self.ypos += dy
                self.__bump = False
            self.score -= 1

        elif self.action == 'shoot':
            if self.arrowinventory > 0:
                self.score -= 10
                self.arrowinventory -= 1
                if dy == 0:
                    if dx  > 0:
                        for x in range(self.xpos, self.gridSize):
                            if self.worldmap[self.ypos][x] == 'wumpus':
                                self.worldmap[self.ypos][x] = 'dead-wumpus'
                                self.score += 500
                                self.__scream = True
                                self.__wumpusCount -= 1
                                self.updatePlace = (x, self.ypos)
                                break
                    else:
                        for x in range(self.xpos, 0, -1):
                            if self.worldmap[self.ypos][x] == 'wumpus':
                                self.worldmap[self.ypos][x] = 'dead-wumpus'
                                self.score += 500
                                self.__scream = True
                                self.__wumpusCount -= 1
                                self.updatePlace = (x, self.ypos)
                                break
                else:
                    if dy  > 0:
                        for y in range(self.ypos, self.gridSize):
                            if self.worldmap[y][self.xpos] == 'wumpus':
                                self.worldmap[y][self.xpos] = 'dead-wumpus'
                                self.score += 500
                                self.__scream = True
                                self.__wumpusCount -= 1
                                self.updatePlace = (self.xpos, y)
                                break
                    else:
                        for y in range(self.ypos, 0, -1):
                            if self.worldmap[y][self.xpos] == 'wumpus':
                                self.worldmap[y][self.xpos] = 'dead-wumpus'
                                self.score += 500
                                self.__scream = True
                                self.__wumpusCount -= 1
                                self.updatePlace = (self.xpos, y)   
                                break
            else:
                self.score -= 1
                self.action = 'wait'

        elif self.action == 'grab':
            if here == 'gold':
                self.worldmap[self.ypos][self.xpos] = 'ground'
                self.score += 1000
                self.updateCurrentPlace = True
                self.__goldCount = 1

        elif self.action == 'climb':
            self.score -= 1
            if self.ypos == 1 and self.xpos == 1:
                self.action = 'end'
                self.score += 500
                return

class Percept():
    def __init__( self, stench, breeze, glitter, bump, scream ):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream

    def __str__( self ):
        return "[stench: " + str(self.stench) + ", breeze: " + str(self.breeze) + ", glitter:  " + str(self.glitter) + ",  bump: " + str(self.bump) + ", scream: " + str(self.scream)+ "]"

class AgentSprite:
    def __init__( self, cellSize, imageTable ):
        self.cellSize = cellSize
        self.myspeed = 0.1
        self.imageTable = imageTable
        self.directionAgentImageTable = ['agentup', 'agentright', 'agentdown', 'agentleft']
        self.agentImageOnCanvas = False
        self.agentdown = Tkinter.PhotoImage(file = 'images/agentdown.gif')
        self.agentdownleft = Tkinter.PhotoImage(file = 'images/agentdownleft.gif')
        self.agentdownright = Tkinter.PhotoImage(file = 'images/agentdownright.gif')
        self.agentright = Tkinter.PhotoImage(file = 'images/agentright.gif')
        self.agentrightleft = Tkinter.PhotoImage(file  ='images/agentrightleft.gif')
        self.agentrightright = Tkinter.PhotoImage(file = 'images/agentrightright.gif')
        self.agentleft = Tkinter.PhotoImage(file = 'images/agentleft.gif')
        self.agentleftright = Tkinter.PhotoImage(file = 'images/agentleftright.gif')
        self.agentleftleft = Tkinter.PhotoImage(file = 'images/agentleftleft.gif')
        self.agentup = Tkinter.PhotoImage(file = 'images/agentup.gif')
        self.agentupright = Tkinter.PhotoImage(file = 'images/agentupright.gif')
        self.agentupleft = Tkinter.PhotoImage(file = 'images/agentupleft.gif')

    def move( self, directionCode, agentcoordx, agentcoordy, canvas ):
        direction = toggleorientation(directionCode)

        if direction == 'down':
            if self.agentImageOnCanvas != False:
                canvas.delete(self.agentImageOnCanvas)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize,
                                           agentcoordy * self.cellSize - 2 * self.cellSize / 3,
                                image = self.agentdownright,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize,
                                           agentcoordy * self.cellSize - self.cellSize / 3,
                                image = self.agentdownleft,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()
            self.agentImageOnCanvas = canvas.create_image(agentcoordx * self.cellSize,
                                                          agentcoordy * self.cellSize,
                                                          image = self.imageTable['agentdown'],
                                                          anchor = Tkinter.NW)
            
        elif direction == 'right':
            if self.agentImageOnCanvas != False:
                canvas.delete(self.agentImageOnCanvas)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize - 2 * self.cellSize / 3,
                                agentcoordy * self.cellSize,
                                image = self.agentrightright,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize - self.cellSize / 3,
                                agentcoordy * self.cellSize,
                                image = self.agentrightleft,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()
            self.agentImageOnCanvas = canvas.create_image(agentcoordx * self.cellSize,
                                                          agentcoordy * self.cellSize,
                                                          image = self.imageTable['agentright'],
                                                          anchor = Tkinter.NW)

        elif direction == 'left':
            if self.agentImageOnCanvas != False:
                canvas.delete(self.agentImageOnCanvas)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize + 2 * self.cellSize / 3,
                                           agentcoordy * self.cellSize,
                                           image = self.agentleftleft,
                                           anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize + self.cellSize / 3,
                                           agentcoordy * self.cellSize,
                                           image = self.agentleftright,
                                           anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()
            self.agentImageOnCanvas = canvas.create_image(agentcoordx * self.cellSize,
                                                          agentcoordy * self.cellSize,
                                                          image = self.imageTable['agentleft'],
                                                          anchor = Tkinter.NW)

        elif direction == 'up':
            if self.agentImageOnCanvas != False:
                canvas.delete(self.agentImageOnCanvas)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize,
                                           agentcoordy * self.cellSize + 2 * self.cellSize / 3,
                                image = self.agentupright,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            tmpImage = canvas.create_image(agentcoordx * self.cellSize,
                                           agentcoordy * self.cellSize + self.cellSize / 3,
                                image = self.agentupleft,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()
            self.agentImageOnCanvas = canvas.create_image(agentcoordx * self.cellSize,
                                                          agentcoordy * self.cellSize,
                                                          image = self.imageTable['agentup'],
                                                          anchor = Tkinter.NW)

    def display( self, direction, agentcoordx, agentcoordy, canvas ):
        # Redraw wumpus
        agentImage = self.directionAgentImageTable[direction]
        if self.agentImageOnCanvas != False:
             canvas.delete(self.agentImageOnCanvas)
        self.agentImageOnCanvas = canvas.create_image(agentcoordx * self.cellSize,
                                                      agentcoordy * self.cellSize,
                                                      image = self.imageTable[agentImage],
                                                      anchor = Tkinter.NW)

# HANDLES ARROW FUNCTIONALITY
class ArrowSprite:
    #Creates constructor.LOADS THE IMAGES INTO VARIABLES SO THAT THEY CAN BE CALLED
    def __init__( self, cellSize ):
        self.arrowx = 0
        self.arrowy = 0
        self.myspeed = 0.1
        self.cellSize = cellSize
        self.arrowright = Tkinter.PhotoImage(file = 'images/arrowright.gif')
        self.arrowleft = Tkinter.PhotoImage(file = 'images/arrowleft.gif')
        self.arrowup = Tkinter.PhotoImage(file = 'images/arrowup.gif')
        self.arrowdown = Tkinter.PhotoImage(file = 'images/arrowdown.gif')
        self.deadwumpus = Tkinter.PhotoImage(file = 'images/dead-wumpus.gif')

    #Determines Orientation for how the arrow should launch
    #up,down,left,right
    def launcharrow( self, directionCode, arrowx, arrowy, canvas ):
        self.myslope = toggleorientation(directionCode)

        #if the orientation is facing down in the self constructor it will allow the arrow to fire up
        if self.myslope == 'down':
            tmpImage = canvas.create_image(arrowx * self.cellSize,
                                           arrowy * self.cellSize,
                                image = self.arrowdown,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()

        elif self.myslope == 'up':
            tmpImage = canvas.create_image(arrowx * self.cellSize,
                                           arrowy * self.cellSize,
                                image = self.arrowup,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()

        elif self.myslope == 'left':
            tmpImage = canvas.create_image(arrowx * self.cellSize,
                                           arrowy * self.cellSize,
                                image = self.arrowleft,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()

        else: #'right':
            tmpImage = canvas.create_image(arrowx * self.cellSize,
                                           arrowy * self.cellSize,
                                image = self.arrowright,
                                anchor = Tkinter.NW)
            canvas.update_idletasks()
            time.sleep(self.myspeed)
            canvas.delete(tmpImage)
            canvas.update_idletasks()

def toggleorientation( direction ):
    if direction == 0:
        return 'up'
    elif direction == 2:
        return 'down'
    elif direction == 1:
        return 'right'
    elif direction == 3:
        return 'left'
