import thread
import threading
import time
import sys, random
import sleekxmpp
import netifaces
from sleekxmpp.xmlstream.stanzabase import ElementBase, JID
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher import StanzaPath
from sleekxmpp.stanza.message import Message

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

class DNS_Msg(ElementBase):
    namespace = 'DNS_setup'
    name = 'DNS'
    plugin_attrib = 'DNS'
    interfaces = set(('setup','query', 'resp','tag'))
    subinterfaces = interfaces

class remoteSignal(ElementBase):
    namespace = 'remote'
    name = 'remote'
    plugin_attrib = 'remote'
    interfaces = set(('setup','type', 'payload'))
    subinterfaces = interfaces

class IpopSignal(ElementBase):
    name = "ipop"
    namespace = "signal"
    plugin_attrib = "ipop"
    interfaces = set(("type", "payload"))

class XmppAgent(sleekxmpp.ClientXMPP):


    def __init__(self, user, pwd, server, controller, device_name = None):
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
        self.add_event_handler("session_start",self.start)
        self.xmpp_handler()


    def handle_presence(self,presence):
        print ("presence received from {} to {} with status {}".format(presence['from'],presence['to'],presence['status']))


    def xmpp_handler(self):
        try:
            self.connect(address = (self.xmpp_host, self.xmpp_port))
            self.process(block=False)
        except:
            print ("exception while connecting to xmpp server.")

    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.add_event_handler("presence_available", self.handle_presence)

    def MSGListener(self, msg):
        setup = str(msg['DNS']['setup'])
        query = str(msg['DNS']['query'])
        response = str(msg['DNS']['resp'])
        tag = str(msg['DNS']['tag'])
        if (setup == "QUERY"):
            print ("received query for {}".format(query))
            if (query.split(".")[2]=="ipop"):
                self.send_response(query, msg['from'])
        elif (setup == "RESP"):
            print ("received response for {} as {}".format(query, response))
            if (query in self.pending_queries.keys()):
                print ("found {} in pending_queries".format(query))
                q_record = self.pending_queries[query]
                print ("QRECORD {}".format(q_record))
                q_record[2] = response
                print (str(type(q_record[1]))+" event after response {}".format(q_record[1]))
                q_record[1].set()
                print ("At agent event {} is {}".format(q_record[1],q_record[1].isSet()))
        elif (setup == "NAME_QUERY"):
            print ("received name query for {}".format(query))
            if (query.split(".")[0]==self.device_name):
                ip_address = self.get_ip()
                self.send_name_query_response(query, response, tag, self.controller)

    def send_query(self, qname, event_item=None):
        self.pending_queries[qname]=[qname, event_item, None]
        msg = self.Message()
        msg['to'] = self.controller
        msg['type'] = 'chat'
        msg['DNS']['setup'] = "QUERY"
        msg['DNS']['query'] = str(qname)
        msg['DNS']['resp'] = "dummy"
        msg['DNS']['tag'] = str(random.getrandbits(40))
        msg.send()

    def send_response(self, qname, sendto):
        msg = self.Message()
        msg['to'] = sendto
        msg['type'] = 'chat'
        msg['DNS']['setup'] = "RESP"
        msg['DNS']['query'] = qname
        msg['DNS']['resp'] = "127.0.0.1"
        msg.send()
        
    def send_name_query_response(self, name_query, response, tag, sendto):
        msg = self.Message()
        msg['to'] = sendto
        msg['type'] = 'chat'
        msg['DNS']['setup'] = "NAME_RESP"
        msg['DNS']['query'] = name_query
        msg['DNS']['resp'] = response
        msg['DNS']['tag'] = tag
        msg.send()

    def send_remote(self,sendto):
        msg = self.Message()
        msg['to'] = sendto
        msg['type'] = 'chat'
        msg['remote']['setup'] = "GCCICC"
        msg['remote']['type'] = "command_control"
        msg['remote']['payload'] = "bob_gnv_gw@xmpp.ipop-project.org"
        msg.send()

    def send_ipop(self,sendto):
        msg = self.Message()
        msg['to'] = sendto
        msg["type"] = "chat"
        msg["ipop"]["type"] = "GCCICC"
        msg["ipop"]["payload"] = "XXXXXXXX"
        msg.send()

    def get_ip(self, iface_name):
        adapters = netifaces.interfaces()
        if (iface_name in adapters):
            addresses = netifaces.ifaddresses(iface_name)
            if (netifaces.AF_INET in addresses.keys()):
                ipaddress = addresses[netifaces.AF_INET][0]["addr"]
                return ipaddress
            else:
                return None
        else:
            return None


if __name__ == '__main__':
    agent = XmppAgent("bob_gnv_gw@xmpp.ipop-project.org","ipop_bob_gw","xmpp.ipop-project.org", "bob_gnv_gw@xmpp.ipop-project.org")
    agent.send_response("pc3.mike.ipop","d1_bob_gnv@xmpp.ipop-project.org")
    agent.send_ipop("d1_bob_gnv@xmpp.ipop-project.org")
    agent.send_remote("d1_bob_gnv@xmpp.ipop-project.org")
