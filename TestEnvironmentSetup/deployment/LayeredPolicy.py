from Graph import *
import random, math
'''Layered topology policy, number of layers is the number of layers except last layer,
distribution is division of linux computes in the middle layers, top layer will always have root node
'''
class LayeredPolicy:
    def __init__(self, cameras, linux_computes, num_layers=2, distribution=[1]):
        self.cameras = cameras
        self.linux_computes = linux_computes
        self.layer_distribution  = distribution
        if (num_layers != len(distribution)+1):
            print("distribution information does not matches with the number of layers specified.")
            exit()
        self.layers = []
        '''the below variables should not be part of class variables, they are temporary'''
        self.linux_compute_feeder = self.create_vertices(self.linux_computes)
        self.camera_feeder = self.create_vertices(self.cameras)
        self.split_into_layers(self.linux_compute_feeder, num_layers)
        '''add the final layer of leaf nodes'''
        self.layers.append(self.camera_feeder)
        print (self.layers)
        self.graph = self.get_graph()
        self.graph.bfs(self.send_tunnel_solicitation)

    ''' graph will call this method at each node while traversing for each of its neighbors'''
    def send_tunnel_solicitation(self, *args):
        print ("sending tunnel solicitation for {} from {} to {} at {}"
               .format(args[0].name, args[0].social_gw, args[1].name, args[1].social_gw))

    '''num layers inclusive of root and penultimate layer, has to be atleast 1.'''
    def split_into_layers(self, input_list, num_layers):
        layer_quantity = []
        layer_quantity.append(1)
        available = len(input_list)-1
        for ratio in self.layer_distribution:
            layer_quantity.append(ratio * available)
        for i in range(num_layers):
            self.layers.append(self.choose(input_list, layer_quantity[i]))


    def create_vertices(self, device_descriptor_list):
        vertex_list = []
        for device_descriptor in device_descriptor_list:
            vertex_list.append(vertex(device_descriptor))
        return vertex_list

    def choose(self, input_list, how_many):
        if (len(input_list)< how_many):
            print("input list has fewer items than needed to be chosen")
            return None
        chosen_items =[]
        for i in range(how_many):
            index = random.randint(0,len(input_list)-1)
            chosen_items.append(input_list[index])
            input_list.remove(input_list[index])
        return chosen_items

    def get_graph(self):
        graph = Graph()
        self.connect_layers(graph ,0)
        return graph

    def connect_layers(self, graph, layer_num):
            if (layer_num == len(self.layers)):
                ''' termination condition, add the leaf nodes and end recursion'''
                return
            elif (layer_num == 0):
                '''special case, initialize root node'''
                graph.root = self.layers[0][0]
                self.connect_layers(graph, layer_num+1)
            else:
                '''normal recursive call, load balanced layering policy, have to connect nodes
                in this layer evenly to nodes in the parent layer.'''
                candidates = self.layers[layer_num]
                parents = self.layers[layer_num-1]
                nodes_per_parent = math.ceil(len(candidates)/len(parents))
                parent_index = 0
                for child_index in range(0, len(candidates)):
                    if ((child_index)%nodes_per_parent == 0 and child_index != 0):
                        parent_index+=1
                    graph.add_edge(parents[parent_index], candidates[child_index])
                self.connect_layers(graph, layer_num+1)



if __name__ == '__main__':
    cameras = [{'info': {'social_gw': 'perso_5@xmpp.ipop-project.org', 'device_type': 'camera'}, 'name': 'camera3'},
               {'info': {'social_gw': 'perso_4@xmpp.ipop-project.org', 'device_type': 'camera'}, 'name': 'camera6'},
               {'info': {'social_gw': 'perso_3@xmpp.ipop-project.org', 'device_type': 'camera'}, 'name': 'camera3'}]
    linux_computes = [{'info': {'social_gw': 'perso_0@xmpp.ipop-project.org', 'device_type': 'linux_computes'},
                       'name': 'linux_computes0'},
                      {'info': {'social_gw': 'perso_1@xmpp.ipop-project.org', 'device_type': 'linux_computes'}, 'name': 'linux_computes0'},
                      {'info': {'social_gw': 'perso_2@xmpp.ipop-project.org', 'device_type': 'linux_computes'}, 'name': 'linux_computes2'}]
    lp = LayeredPolicy(cameras, linux_computes)
