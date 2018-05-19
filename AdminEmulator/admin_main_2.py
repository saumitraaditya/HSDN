# generic imports
import threading
import time
import sys, random, json, pprint
from Utilities import *

# sleekxmpp specific imports
import sleekxmpp
from sleekxmpp.xmlstream.stanzabase import ElementBase, JID
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher import StanzaPath
from sleekxmpp.stanza.message import Message




class DNS_Msg(ElementBase):
    namespace = 'DNS_setup'
    name = 'DNS'
    plugin_attrib = 'DNS'
    interfaces = set(('setup', 'query', 'resp', 'tag'))
    subinterfaces = interfaces


class remoteSignal(ElementBase):
    namespace = 'remote'
    name = 'remote'
    plugin_attrib = 'remote'
    interfaces = set(('setup', 'type', 'payload'))
    subinterfaces = interfaces


class IpopSignal(ElementBase):
    name = "ipop"
    namespace = "signal"
    plugin_attrib = "ipop"
    interfaces = set(("type", "payload"))

class NetworkSetup(ElementBase):
    name = "n_setup"
    namspace = "n_setup"
    plugin_attrib = "n_setup"
    interfaces = set(("payload", "tag"))
    subinterfaces = interfaces



class SocialAgent(sleekxmpp.ClientXMPP):

    def __init__(self, user, pwd, server, controller=None, device_name=None):
        self.server_name = server
        self.controller = controller
        self.device_name = device_name
        self.pending_queries = {}
        self.xmpp_host = server
        self.xmpp_port = 5222
        sleekxmpp.ClientXMPP.__init__(self, user, pwd)
        register_stanza_plugin(Message, DNS_Msg)
        register_stanza_plugin(Message, remoteSignal)
        register_stanza_plugin(Message, IpopSignal)
        self.register_handler(
            Callback('DNS',
                     StanzaPath('message/DNS'),
                     self.MSGListener)
        )
        self.register_handler(
            Callback('n_setup',
                     StanzaPath('message/n_setup'),
                     self.MSGListener)
        )
        self.add_event_handler("session_start", self.start)
        self.xmpp_handler()

    def handle_presence(self, presence):
        print ("presence received from {} to {} with status {}".format(presence['from'], presence['to'],
                                                                       presence['status']))
        pprint(self.client_roster)

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
        pprint(self.client_roster)


    def MSGListener(self, msg):
        payload = str(msg['n_setup']['payload'])
        tag = str(msg['n_setup']['tag'])
        pprint(payload)

    def send_n_setup(self, sendto):
        msg = self.Message()
        msg["to"] = sendto
        msg['type'] = 'chat'
        msg['remote']['tag'] = "4636736556365765765756356"
        msg['remote']['payload'] = str({"name":"saumitra"})
        msg.send()

    def send_remote(self, sendto):
        msg = self.Message()
        msg['to'] = sendto
        msg['type'] = 'chat'
        msg['remote']['setup'] = "GCCICC"
        msg['remote']['type'] = "command_control"
        msg['remote']['payload'] = "bob_gnv_gw@xmpp.ipop-project.org"
        msg.send()

    def send_ipop(self, sendto):
        msg = self.Message()
        msg['to'] = sendto
        msg["type"] = "chat"
        msg["ipop"]["type"] = "GCCICC"
        msg["ipop"]["payload"] = "XXXXXXXX"
        msg.send()




if __name__ == '__main__':
    # agent = SocialAgent("bob_gnv_gw@xmpp.ipop-project.org", "ipop_bob_gw", "xmpp.ipop-project.org",
    #                   "bob_gnv_gw@xmpp.ipop-project.org")
    # agent.send_response("pc3.mike.ipop", "d1_bob_gnv@xmpp.ipop-project.org")
    # agent.send_ipop("d1_bob_gnv@xmpp.ipop-project.org")
    # agent.send_remote("d1_bob_gnv@xmpp.ipop-project.org")
    # loadTemplate(path="./template-one.json")
    agent = SocialAgent("jude_gw@xmpp.ipop-project.org","jude_gw","xmpp.ipop-project.org")


