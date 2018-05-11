# -*- coding: utf-8; mode: python -*-
#
# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#

#
# @author Régis Clouard.
#

# @file utils.py
#

## code to handle timeouts
import signal
import heapq

class TimeoutFunctionException( Exception ):
    """Exception to raise on a timeout"""
    pass

class TimeoutFunction:
    
    def __init__( self, function, timeout ):
        "timeout must be at least 1 second."
        self.timeout = timeout
        self.function = function

    def handle_timeout( self, signum, frame ):
        raise TimeoutFunctionException()

    def __call__( self, *args ):
        if not 'SIGALRM' in dir(signal):
            return self.function(*args)
        old = signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.timeout)
        try:
            result = self.function(*args)
        finally:
            signal.signal(signal.SIGALRM, old)
        signal.alarm(0)
        return result


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """
    def  __init__( self ):
        self.heap = []

    def push( self, item, priority ):
        pair = (priority,item)
        heapq.heappush(self.heap,pair)

    def pop( self ):
        return heapq.heappop(self.heap)

    def isEmpty( self ):
        return len(self.heap) == 0
