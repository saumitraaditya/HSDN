import json, pprint
import argparse
from pathlib import Path
import random

'''tailored to my use case no general features.'''



class configurationFactory():

    def __init__(self, social_template_file, resources_template_file):
        if (Path(social_template_file).exists() and Path(resources_template_file).exists):
            with open(social_template_file) as social_template:
                try:
                    self.social_template = json.load(social_template)
                except:
                    print("malformed json file {}".format(social_template_file))
                    exit()
            with open(resources_template_file) as resource_template:
                try:
                    self.resource_template = json.load(resource_template)
                except:
                    print("malformed json file {}".format(resources_template_file))
                    exit()
            self.config_dir = Path(Path.cwd(),'configs')
            if ( not self.config_dir.exists()):
                self.config_dir.mkdir()
        else:
            print("check template json file paths, could not find a valid path.")

    ''' generate ipop configuration files using the given base user name'''
    def __init__(self, ipop_base_file_path, base_username = None, num_configs = None):
        if (Path(ipop_base_file_path).exists() and base_username != None and num_configs != None):
            with open(ipop_base_file_path) as ipop_template:
                try:
                    self.ipop_template = json.load(ipop_template)
                except:
                    print("malformed json file {}".format(ipop_template))
                    exit()
            self.config_dir = Path(Path.cwd(),'ipop-configs')
            if (not self.config_dir.exists()):
                self.config_dir.mkdir()
            self.create_ipop_config(base_username, num_configs)
        else:
            print("check template json file paths, could not find a valid path.")


    def create_ipop_config(self, base_username, num_configs, bridge_name = "ipopbr0", base_ip = "10.10.10.100"):
        overlay = self.ipop_template["CFx"]["Overlays"][0]
        domain_name = self.ipop_template["Signal"]["Overlays"][overlay]["HostAddress"]
        self.ipop_template["BridgeController"]["Overlays"][overlay]["BridgeName"] = bridge_name
        ip = base_ip.split(".")
        last_octet = int(ip[3])
        base_ip = ""
        for octet in ip[0:-1]:
            base_ip += octet+"."
        for i in range(num_configs):
            user = base_username+str(i)
            self.ipop_template["Signal"]["Overlays"][overlay]["Username"] = user+"@"+domain_name
            self.ipop_template["Signal"]["Overlays"][overlay]["Password"] = user
            self.ipop_template["BridgeController"]["Overlays"][overlay]["IP4"] = base_ip + str(last_octet+i)
            self.generate_json( self.ipop_template, file_name = "ipop_config_"+str(i)+".json")


    '''will create social account configuration files.'''
    def create_social_config(self):
        num_nodes = self.social_template["num_nodes"]
        leading_id = self.social_template["leading_id"]
        domain_name = self.social_template["domain"]
        for i in range(num_nodes):
            social_config = {}
            social_config["username"] = leading_id+str(i)+"@"+domain_name
            social_config["password"] = leading_id+str(i)
            social_config["server"] = domain_name
            self.generate_json(social_config, file_name="social_config_"+str(i)+".json")

    '''will create resource configuration files. Initially one peer just volunteers one resource'''
    def create_static_resources(self):
        resources=[]
        for (k,v) in self.resource_template.items():
            for i in range(v):
                resources.append(k)
        num_nodes = len(resources)
        for i in range(num_nodes):
            resource_data = {}
            resource_data[resources[i]+str(random.randint(0,num_nodes))]=dict(device_type=resources[i])
            self.generate_json(resource_data, file_name="resource_config_"+str(i)+".json")

    def generate_json(self, data, file_name=None):
        # pprint.pprint(data)
        filename = self.config_dir.joinpath(file_name)
        filename.write_text(json.dumps(data))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", dest="social", help="social account template")
    parser.add_argument("-r", dest="resources", help="static resource template")
    parser.add_argument("-i", dest="ipop", help="ipop base configuration")
    args = parser.parse_args()
    if (args.social != None  and args.resources != None):
        cf = configurationFactory(args.social, args.resources)
        cf.create_social_config()
        cf.create_static_resources()
    elif (args.ipop != None):
        cf = configurationFactory(args.ipop, base_username="perso_", num_configs=5)