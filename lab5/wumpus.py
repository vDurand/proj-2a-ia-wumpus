#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1
#

#
# @file wumpus.py
#
# @author Régis Clouard
#

import sys
import random
from wumpusworld import WumpusFrame

class Wumpus:
    def __init__( self, solver, function = None ):
        self.__solver = solver
        self.__heuristicFunction = function

def runAgents( agent, speed, width, timeout, debugging ):
    """ The real main. """
    if debugging >= 0:
        random.seed(debugging);
    agent.init(width)
    frame = WumpusFrame(width, speed, agent)
    frame.mainloop()
    print("Score:", frame.tw.score)

def default( str ):
    return str + ' [Default: %default]'

def readCommand( argv ):
    """ Processes the command used to run Wumpus from the command line. """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python wumpus.py <options>
    EXAMPLES:   python wumpus.py --agent DummyAgent
                OR  python wumpus.py -a DummyAgent
                    - run wumpus with the dummy agent
    """
    parser = OptionParser(usageStr)
    
    parser.add_option('-a', '--agent', dest = 'agent',
                      help = default('the agent to use'),
                      metavar = 'TYPE', default = 'DummyAgent')
    parser.add_option('-w', '--width', dest  ='width',
                      help = default('World width'), default = 4)
    parser.add_option('-s', '--speed', dest  ='speed',
                      help = default('Speed'), default = 70)
    parser.add_option('-t', '--timeout', dest='timeout',
                      help = default('Maximum search time (for debugging purpose)'), default = 2000)
    parser.add_option('-g', '--debugging', dest = 'debugging',
                      help = 'For debuging purpose, set the random seed which generates the same world with the same seed', default = -1)
    
    options, otherjunk = parser.parse_args(argv)

    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()
    
    # Choose a Wumpus solver
    try:
        module = __import__('agent')
        if options.agent in dir(module):
            agent = getattr(module, options.agent)
            args['agent'] = agent()
        else:
            raise Exception('Unknown agent: ' + options.agent)
    except ImportError:
        raise Exception('No file agent.py')
    
    args['width'] = int(options.width) + 2 # Add the borders.
    args['speed'] = int(options.speed)
    args['timeout'] = int(options.timeout)
    args['debugging'] = options.debugging

    return args

if __name__ == '__main__':
    """ The main function called when wumpus.py is run
    from the command line:

    > python wumpus.py

    See the usage string for more details.

    > python wumpus.py --help
    > python wumpus.py -h """
    args = readCommand( sys.argv[1:] ) # Get game components based on input
    print "\n-------------------------------------------------------"
    for arg in sys.argv:
        print arg,
    print "\n-------------------------------------------------------"
    runAgents( **args )
