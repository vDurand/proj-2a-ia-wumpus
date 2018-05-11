#! /usr/bin/python
# -*- coding: utf-8; mode: python -*-
#
# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1
#

#
# @file agents.py
#
# @author Régis Clouard.
# @student Valentin Durand
# @student Sami Elyadari
#

import random
import copy

COST_ARROW = 10
PTS_GOLD = 1000
PTS_WUMPUS = 500
COST_DEATH = 1000
PTS_LEAVE = 500
COST_MOVE = 1

class Agent:
    """
    The base class for various flavors of the agent.
    This an implementation of the Strategy design pattern.
    """
    def think( self, percept ):
        raise Exception, "Invalid Agent class, think() not implemented"

    def init( self, gridSize ):
        raise Exception, "Invalid Agent class, init() not implemented"

class DummyAgent( Agent ):
    """
    An example of simple Wumpus hunter brain: acts randomly...
    """

    def init( self, gridSize ):
        pass

    def think( self, percept ):
        return random.choice(['shoot', 'grab', 'left', 'right', 'forward', 'forward'])

class gameState():
    def __init__(self, size, map):
        self._size = size
        self._score = 0
        self._map = map
        self._current = {'x':0,'y':0}
        self._direction = 'r'
        self._wumpusDead = False
        self._hasArrow = True
        self._hasGold = False
        self._glitter = False
        self._over = False

    def makeMove(self, move):
        #print "makemove=",move
        self._score = self._score - COST_MOVE
        if(move == 'left'):
            if(self._direction == 'r'):
                self._direction = 'u'
            elif(self._direction == 'u'):
                self._direction = 'l'
            elif(self._direction == 'l'):
                self._direction = 'd'
            elif(self._direction == 'd'):
                self._direction = 'r'
        elif(move == 'right'):
            if(self._direction == 'r'):
                self._direction = 'd'
            elif(self._direction == 'd'):
                self._direction = 'l'
            elif(self._direction == 'l'):
                self._direction = 'u'
            elif(self._direction == 'u'):
                self._direction = 'r'
        elif(move == 'forward'):
            if(self._direction == 'r'):
                self._current['y'] = self._current['y'] + 1
            elif(self._direction == 'd'):
                self._current['x'] = self._current['x'] + 1
            elif(self._direction == 'l'):
                self._current['y'] = self._current['y'] - 1
            elif(self._direction == 'u'):
                self._current['x'] = self._current['x'] - 1
        elif(move == 'shoot'):
            self._hasArrow = False
            self._score = self._score - COST_ARROW
        elif(move == 'climb'):
            self._over = True
            self._score = self._score + PTS_LEAVE
        elif(move == 'grab'):
            self._hasGold = True
            self._score = self._score + PTS_GOLD

    def getLegalAction(self):
        legalActions = ['left','right']
        if(self._glitter == True):
            legalActions.append('grab')
        if(self._current['x'] == 0 and self._current['y'] == 0):
            legalActions.append('climb')
        if(self._hasArrow == True):
            legalActions.append('shoot')
        if(self._direction == 'r'):
            if self._current['y'] < self._size - 1:
                legalActions.append('forward')
        if(self._direction == 'u'):
            if self._current['x'] > 0:
                legalActions.append('forward')
        if(self._direction == 'l'):
            if self._current['y'] > 0:
                legalActions.append('forward')
        if(self._direction == 'd'):
            if self._current['x'] < self._size - 1:
                legalActions.append('forward')

        if(self._current['x'] == 0 and self._current['y'] == 0):
            if self._direction == 'd':
                legalActions.remove('right')
            if self._direction == 'r':
                legalActions.remove('left')
        if(self._current['x'] == self._size-1 and self._current['y'] == self._size-1):
            if self._direction == 'u':
                legalActions.remove('right')
            if self._direction == 'l':
                legalActions.remove('left')
        if(self._current['x'] == 0 and self._current['y'] == self._size-1):
            if self._direction == 'd':
                legalActions.remove('left')
            if self._direction == 'l':
                legalActions.remove('right')
        if(self._current['x'] == self._size-1 and self._current['y'] == 0):
            if self._direction == 'u':
                legalActions.remove('left')
            if self._direction == 'r':
                legalActions.remove('right')
        #print "legalactions=",legalActions
        return legalActions

    def updateProba(self, percept):
        possible = []

        if self._current['x']+1 < 0 or self._current['x']+1 > self._size:
            new = {'x':self._current['x']+1,'y':self._current['y']}
            if self._map[new['x']][new['y']]['safe'] != 1:
                possible.append(new)
        if self._current['x']-1 < 0 or self._current['x']-1 > self._size:
            new = {'x':self._current['x']-1,'y':self._current['y']}
            if self._map[new['x']][new['y']]['safe'] != 1:
                possible.append(new)
        if self._current['y']+1 < 0 or self._current['y']+1 > self._size:
            new = {'x':self._current['x'],'y':self._current['y']+1}
            if self._map[new['x']][new['y']]['safe'] != 1:
                possible.append(new)
        if self._current['y']-1 < 0 or self._current['y']-1 > self._size:
            new = {'x':self._current['x'],'y':self._current['y']-1}
            if self._map[new['x']][new['y']]['safe'] != 1:
                possible.append(new)
        #print "x=",self._current['x']," y=",self._current['y']
        self._map[self._current['x']][self._current['y']]['safe'] = 1

        if percept.stench:
            for i in possible:
                if self._map[i['x']][i['y']]['wumpus'] > 0:
                    self._map[i['x']][i['y']]['wumpus'] = 1
                else:
                    self._map[i['x']][i['y']]['wumpus'] = 1/len(possible)
        if percept.breeze:
            for i in possible:
                if self._map[i['x']][i['y']]['pit'] > 0:
                    self._map[i['x']][i['y']]['pit'] = 1
                else:
                    self._map[i['x']][i['y']]['pit'] = 1/len(possible)
            
        if percept.glitter:
            self._hasGold = True

        if percept.scream:
            self._score = self._score + PTS_WUMPUS
            self._wumpusDead = True
            for i in range (self._size):
                for j in range (self._size):
                    self._map[i][j]['wumpus'] = 0

    def finishingPosition(self):
        if self._hasGold and self._wumpusDead and self._current['x'] == 0 and self._current['y'] == 0:
            return True
        return False

    def seekWumpusPos(self):
        res = {}
        for i in range (self._size):
            for j in range (self._size):
                if self._map[i][j]['wumpus'] == 1:
                    res[0] = i
                    res[1] = j
        return res

    def generateSuccessor(self, action):
        state = copy.deepcopy(self)
        state.makeMove(action)
        if(action == 'shoot'):
            probableWumpusPos = state.seekWumpusPos()
            if len(probableWumpusPos) > 0:
                if state._current['x'] == probableWumpusPos[0] or state._current['y'] == probableWumpusPos[1]:
                    state._wumpusDead = True
                    state._score = state._score + PTS_WUMPUS
            # 1/N chance that the wumpus is on the same column or row with N the number of rows
            elif random.randint(0,100) < (1/self._size)*100:
                state._wumpusDead = True
                state._score = state._score + PTS_WUMPUS
            
            
            
        if(action == 'forward'):
            # 1/(N*N) chance to find the gold
            if random.randint(0,100) < (1/(self._size*self._size))*100:
                state.makeMove('grab')
            # 1/10 chance to fall in a pit
            elif random.randint(0,100) < (1/10)*100:
                state._score = state._score - COST_DEATH
                state._over = True
            # 1/(N*N) chance to meet the wumpus
            elif random.randint(0,100) < (1/(self._size*self._size))*100:
                state._score = state._score - COST_DEATH
                state._over = True

        return state

#######
####### Exercise 1: Goal-Based Agent
#######
class GoalBasedAgent( Agent ):
    """
    Your smartest Wumpus hunter brain.
    """
    def init( self, gridSize ):
        map = []
        for i in range (gridSize-2):
            new = []
            for j in range (gridSize-2):
                new.append({'safe':0,'pit':0,'wumpus':0})
            map.append(new)
        self._currentState = gameState(gridSize-2, map)

    def think( self, percept ):
        """
        Returns the best action regarding the current state of the game.
        Available actions are [LEFT, RIGHT, FORWARD, SHOOT, GRAB, CLIMB].
        Note that thinking time is limited to 1 second.
        """
        self._currentState.updateProba(percept)
        #print "direction=",self._currentState._direction
        
        if percept.glitter:
            self._currentState.makeMove('grab')
            return 'grab'

        if self._currentState.finishingPosition() == True:
            self._currentState.makeMove('climb')
            return 'climb'
        
        nextMove = self.getAction()
        self._currentState.makeMove(nextMove)
        return nextMove

    def getAction( self ):
        #print "starting getAction"
        depth = 2
        legalActions = self._currentState.getLegalAction()
        nextStates = [self._currentState.generateSuccessor(action) for action in legalActions]
        v = [self.expectimax(1, nextGameState, depth - 1) for nextGameState in nextStates] 
        maxV = max(v)
        listMax = []
        # Get the index of maxV
        for i in range(0, len(v)):
            if v[i] == maxV:
                listMax.append(i)
        # random when there is a tie
        i = random.randint(0, len(listMax) - 1)
        action = legalActions[listMax[i]]
        print "--> action found = ", action
        return action

    def expectimax( self, agentIndex, gameState, depth ):
        #print "starting expectimax"
        if gameState._over == True or depth == 0:
            return gameState._score
        else:
            legalActions = gameState.getLegalAction()
            nextStates = [gameState.generateSuccessor(action) for action in legalActions]
            if agentIndex == 0:
                return max([self.expectimax(1 - agentIndex, nextState, depth - 1) for nextState in nextStates])
            else:
                return sum([self.expectimax(1 - agentIndex, nextState, depth - 1) for nextState in nextStates])