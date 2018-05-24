# generic imports
import threading
import time
import sys, random, json, pprint
from Utilities import *
from Task import Task

# sleekxmpp specific imports
import sleekxmpp
from sleekxmpp.xmlstream.stanzabase import ElementBase, JID
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher import StanzaPath
from sleekxmpp.stanza.message import Message

class remoteSignal(ElementBase):
    namespace = 'remote'
    name = 'remote'
    plugin_attrib = 'remote'
    interfaces = set(('setup', 'type', 'payload','tag'))
    subinterfaces = interfaces


class SocialAgent(sleekxmpp.ClientXMPP):

    def __init__(self, user, pwd, server, controller=None, device_name=None):
        self.server_name = server
        self.controller = controller
        self.device_name = device_name
        self.pending_queries = {}
        self.xmpp_id = user
        self.xmpp_host = server
        self.xmpp_port = 5222
        sleekxmpp.ClientXMPP.__init__(self, user, pwd)
        register_stanza_plugin(Message, remoteSignal)
        self.register_handler(
            Callback('remote',
                     StanzaPath('message/remote'),
                     self.MSGListener)
        )
        self.add_event_handler("session_start", self.start)
        self.xmpp_handler()

        # resource_file, is a dict that keeps track of my local resources.
        # self.resources = {}
        # self.get_my_resources()
        # self._task = None

    def handle_presence(self, presence):
        print ("presence received from {} to {} with status {}".format(presence['from'], presence['to'],
                                                                       presence['status']))
        # pprint(self.client_roster['jude_gw@xmpp.ipop-project.org']['subscription'])
        # self.broadcast_request()

    def xmpp_handler(self):
        try:
            self.connect(address=(self.xmpp_host, self.xmpp_port))
            self.process(block=False)
        except:
            print ("exception while connecting to xmpp server.")

    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.add_event_handler("presence_available", self.handle_presence)

    def broadcast_request(self):
        for friend in self.client_roster.keys():
            if (self.client_roster[friend]['subscription']=='both'):
                self.send_n_setup(friend)

    def MSGListener(self, msg):
        setup = msg['remote']['setup']
        payload = msg['remote']['payload']
        print("received a message of type {}".format(setup))
        if (setup == "resource_solicitation"):
            task_description = json.loads(payload)
            task_initiator = task_description["initiator"]
            pprint(task_description)
            '''for testing if I have the requested resource I 
            simply voulunteer it.'''
            solicited_device_types = task_description["devices_needed"]
            for device_type in solicited_device_types:
                if (device_type in self.resources and len(self.resources[device_type])!=0):
                    print ("device of type {} is available.".format(device_type))
                    self.send_remote(setup="solicitation_response", msg_type="device_volunteer",\
                                     payload=json.dumps(self.resources[device_type][0]),sendto=task_initiator)

        elif (setup=="solicitation_response"):
            response = json.loads(payload)
            device_type = response["info"]["device_type"]
            print("received solicitation response from {} for device type {}".\
                  format(msg['from'], device_type ))
            print(self._task.description)
            print(type(self._task.description))
            self._task.description[device_type].append(response)
            print(self._task.description)



    def initiate_task(self, file_path):
        template = loadJsonFile(path=file_path)
        self._task = Task(template)
        self._task.description["initiator"] = self.xmpp_id
        self.send_remote(setup="resource_solicitation", msg_type="task_template",\
                         payload=json.dumps(template),sendto="janice_gw@xmpp.ipop-project.org")

    def send_remote(self, setup, msg_type, payload, sendto=None):
        print("received payload is {}".format(payload))
        msg = self.Message()
        msg['to'] = sendto
        msg['type'] = 'chat'
        msg['remote']['setup'] = setup
        msg['remote']['type'] = msg_type
        msg['remote']['payload'] = payload
        msg['remote']['tag'] = str(7584758475827)
        msg.send()

    '''This method will eventually get all the resources on 
    the PLO that this admin component is responsible for, in the final version
    this could be done by sending messages over the social network.'''
    def get_my_resources(self):
        resources = loadJsonFile(path="static_resources.json")
        for device_name in resources:
            device_type = resources[device_name]["device_type"]
            if  device_type not in self.resources:
                self.resources[device_type] = []
            self.resources[device_type].append({"name":device_name, "info":resources[device_name]})
            pprint(self.resources)


    '''instruct the social gateway to allow dns name resolution request for device_name 
    from a social peer to to proceed. {'device_name':'name of the device','social_peer':'social peers name'}'''
    def allow_access(self,request):
        self.send_remote(setup="allow_access", msg_type="allow_access", \
                         payload=json.dumps(request), sendto=self.xmpp_id)

    '''Instruct social gateway to open a specific port for a given social peer'''
    def open_port(self, port_open, peer_social_gateway):
        self.send_remote(setup="open_port", msg_type="open_port", payload=json.dumps({"peer":peer_social_gateway,"port":port_open}), sendto=self.xmpp_id)

    ''' Instructs ipop component on social gateway to create a tunnel to remote peers gateway.'''
    def create_tunnel(self, peer_social_gateway):
        self.send_remote(setup="tunnel_creation", msg_type="tunnel_creation", \
                         payload=peer_social_gateway, sendto=self.xmpp_id)

    '''
        solicits remote social admin (target) to create a tunnel to a social peer's social gateway 
       request is a json that contains some meta information, such
       as task identifier.
       {"task_identifier:"45445e5t4r4t5e4y54y545ytuu73w", "social_peer":"social_peer"}
    '''
    def tunnel_solicitation(self, request, target):
        self.send_remote(setup="tunnel_solicitation", msg_type="tunnel_solicitation",
                         payload=json.dumps(request), sendto=target)



if __name__ == '__main__':
    # agent = SocialAgent("bob_gnv_gw@xmpp.ipop-project.org", "ipop_bob_gw", "xmpp.ipop-project.org",
    #                   "bob_gnv_gw@xmpp.ipop-project.org")
    # agent.send_response("pc3.mike.ipop", "d1_bob_gnv@xmpp.ipop-project.org")
    # agent.send_ipop("d1_bob_gnv@xmpp.ipop-project.org")
    # agent.send_remote("d1_bob_gnv@xmpp.ipop-project.org")
    # loadTemplate(path="./template-one.json")
    agent = SocialAgent("perso_1@xmpp.ipop-project.org","perso_1","xmpp.ipop-project.org")
    # agent.initiate_task("/home/osboxes/AdminEmulator/template-one.json")
    agent.create_tunnel("perso_0@xmpp.ipop-project.org")



