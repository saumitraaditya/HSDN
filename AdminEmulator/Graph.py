
'''We do adjacency list representation of the graph.'''

from queue import Queue
from collections import defaultdict

class vertex:
    def __init__(self, device_descriptor):
        self.name = device_descriptor['name']
        self.social_gw = device_descriptor['info']['social_gw']
        self.device_type = device_descriptor['info']['device_type']
        

class Graph:
    def __init__(self):
        self.root = None
        self._graph = {}


    '''adds a bidirectional edge.'''
    def add_edge(self, source, target):
        if (source not in self._graph.keys()):
            self._graph[source] = []
        if (target not in self._graph.keys()):
            self._graph[target] = []
        self._graph[source].append(target)
        self._graph[target].append(source)

    ''' do a bfs traversal of the graph, and invoke the method at_each_node at every node'''
    def bfs(self, at_each_node):
        v_queue = Queue()
        visited = defaultdict(lambda:False)
        v_queue.put(self.root)
        visited[self.root] = True
        while (not v_queue.empty()):
            curr_v = v_queue.get()
            visited[curr_v] = True
            for neighbor in self._graph[curr_v]:
                at_each_node(curr_v, neighbor)
                if (not visited[neighbor]):
                    v_queue.put(neighbor)
