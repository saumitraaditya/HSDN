import json, pprint
import argparse
import time
from pathlib import Path
import random, shutil
import traceback
import paramiko
from paramiko import SSHClient
'''tailored to my use case no general features.'''



class configurationFactory():

    def __init__(self, **kwargs):
        if (kwargs["type"] == "social"):
            social_template_file = kwargs["social_template_file"]
            resources_template_file = kwargs["resource_template_file"]
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
                self.config_dir = Path(Path.cwd(), 'configs')
                if (not self.config_dir.exists()):
                    self.config_dir.mkdir()
            else:
                print("check template json file paths, could not find a valid path.")
        elif (kwargs["type"] == "ipop"):
            ipop_base_file_path = kwargs["ipop_base_file_path"]
            base_username = kwargs["base_username"]
            num_configs = kwargs["num_configs"]
            if (Path(ipop_base_file_path).exists() and base_username != None and num_configs != None):
                with open(ipop_base_file_path) as ipop_template:
                    try:
                        self.ipop_template = json.load(ipop_template)
                    except:
                        print("malformed json file {}".format(ipop_template))
                        exit()
                self.config_dir = Path(Path.cwd(), 'ipop-configs')
                if (not self.config_dir.exists()):
                    self.config_dir.mkdir()
                self.create_ipop_config(base_username, num_configs)
            else:
                print("check template json file paths, could not find a valid path.")

        elif (kwargs["type"] == "generic"):
            template_path = kwargs["template_path"]
            if (Path(template_path).exists()):
                with open(template_path) as template_file:
                    try:
                        self.custom_template = json.load(template_file)
                        self.arg_dict = {}
                        self.arg_dict["config_type"] = self.custom_template["config_type"]
                        self.arg_dict["base_file"] = self.custom_template["base_file"]
                        self.arg_dict["base_user"] = self.custom_template["base_user"]
                        self.arg_dict["server"] = self.custom_template["server"]
                        self.arg_dict["num_nodes"] = self.custom_template["num_nodes"]
                    except:
                        print("malformed json file {}".format(template_path))
                        exit()
            if (self.arg_dict["config_type"] == "osnBridge"):
                self.create_onos_osnBridge_config(self.arg_dict)
            elif (self.arg_dict["config_type"] == "dns"):
                self.create_dns_config(self.arg_dict)
            elif (self.arg_dict["config_type"] == "dhcp"):
                self.create_onos_dhcp_config(self.arg_dict)

        elif (kwargs["type"] == "remote"):
            remoteinfo_config = kwargs["remoteinfo_config"]
            self.rcd(remoteinfo_config)

    def create_ipop_config(self, base_username, num_configs, bridge_name = "CLO-br", base_ip = "10.10.10.100"):
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

    '''will create resource configuration files. Initially one peer just volunteers one resource, initial plan was to
    give devices unique names but since experiment assumes one device per peer, we can have the same name it also sim
    plifies naming of interfaces in the experimental setup.'''
    def create_static_resources(self):
        resources=[]
        for (k,v) in self.resource_template.items():
            for i in range(v):
                resources.append(k)
        num_nodes = len(resources)
        # for i in range(num_nodes):
        #     resource_data = {}
        #     resource_data[resources[i]+str(random.randint(0,num_nodes))]=dict(device_type=resources[i])
        #     self.generate_json(resource_data, file_name="resource_config_"+str(i)+".json")
        for i in range(num_nodes):
            resource_data = {}
            if (resources[i]=="linux_computes"):
                dev_name = "compute"
            elif (resources[i]=="camera"):
                dev_name = "camera"
            resource_data[dev_name]=dict(device_type=resources[i])
            self.generate_json(resource_data, file_name="resource_config_"+str(i)+".json")


    def generate_json(self, data, file_name=None):
        # pprint.pprint(data)
        filename = self.config_dir.joinpath(file_name)
        filename.write_text(json.dumps(data))

    def remote_invocation(self):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("apt071.apt.emulab.net", 25810, "sam")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('sudo docker container ls')
        print(ssh_stdout.read())
        sftp = ssh.open_sftp()
        sftp.put('remote_config.zip', '/mnt/mydrive/remote_config.zip')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('unzip remote_config.zip')

    ''' will receive sshclient reference of the remote machine'''
    def execute_remotely(self, sshclient, sftp, index, infile):
        config_archive = self.create_remote_config_folder(infile, index=index)
        sftp.put(config_archive, '/mnt/mydrive/remote_config.zip')
        sshclient.exec_command('cd /mnt/mydrive/; unzip remote_config.zip')
        ssh_stdin, ssh_stdout, ssh_stderr= sshclient.exec_command('cd /local/scripts/; sudo nohup sudo ./postConfigUpload.sh &')

    ''' will parse json file from cloudlab to extract node login information'''
    def parse_nodes(self, json_input_file):
        pass

    def rcd(self, json_file):
        folder = self.create_remote_config_folder(json_file)

    ''' this method will create a folder containing executables and configuration for remote test node
    will need
    1. create root application folder
    2. copy all relevant configuration files
    '''
    def create_remote_config_folder(self, in_file, index=0):

        if (not Path(in_file).exists()):
            print("path {} given is not valid".format(in_file))
            exit()
        try:
            with open(in_file) as argument_file:
                try:
                    arguments = json.load(argument_file)
                except:
                    print("malformed json file {}".format(argument_file))
                    exit()
            resource_config = arguments["admin-resource"] + str(index) + ".json"
            social_config_admin = arguments["admin-social"] + str(index) + ".json"
            dns_config = arguments["dns"]+ str(index) + ".json"
            ipop_config = arguments["ipop-config"]+ str(index) + ".json"
            onos_dhcp_config = arguments["onos-dhcp"]+ str(index) + ".json"
            onos_osnBridge_config = arguments["onos-social"]+ str(index) + ".json"
        except Exception:
            print(traceback.format_exc())


        remote_config_dir = Path(Path.cwd(), 'remote-config')
        if (remote_config_dir.exists()):
            shutil.rmtree(remote_config_dir.as_posix())

        remote_config_dir.mkdir()
        shutil.copy(resource_config, Path(remote_config_dir,'static-resources.json').as_posix())
        shutil.copy(ipop_config, Path(remote_config_dir, 'ipop-config.json').as_posix())
        shutil.copy(social_config_admin, Path(remote_config_dir, 'social-config-admin.json').as_posix())
        shutil.copy(dns_config, Path(remote_config_dir, 'dns-config.json').as_posix())
        shutil.copy(onos_dhcp_config, Path(remote_config_dir, 'onos-dhcp-config.json').as_posix())
        shutil.copy(onos_osnBridge_config, Path(remote_config_dir, 'onos-osnBridge-config.json').as_posix())
        shutil.make_archive("remote_config", 'zip', remote_config_dir.as_posix())
        return Path(Path.cwd(),"remote_config.zip").as_posix()
    '''for now lets have all social domains use same subnet'''
    def create_onos_dhcp_config(self, kwargs):
        base_file = kwargs["base_file"]
        num_nodes = int(kwargs["num_nodes"])
        if (Path(base_file).exists()  and num_nodes != None):
            with open(base_file) as template_file:
                try:
                    template = json.load(template_file)
                except:
                    print("malformed json file {}".format(template))
                    exit()
            self.config_dir = Path(Path.cwd(),'onos_dhcp_configs')
            if (not self.config_dir.exists()):
                self.config_dir.mkdir()
            for i in range(num_nodes):
                self.generate_json(template, file_name="onos_dhcp_config_" + str(i) + ".json")
        else:
            print("check template json file paths, could not find a valid path.")

    def create_onos_osnBridge_config(self, kwargs):
        base_file = kwargs["base_file"]
        base_user = kwargs["base_user"]
        server = kwargs["server"]
        num_nodes = int(kwargs["num_nodes"])
        if (Path(base_file).exists() and  num_nodes != None):
            with open(base_file) as template_file:
                try:
                    template = json.load(template_file)
                except:
                    print("malformed json file {}".format(template))
                    exit()
            self.config_dir = Path(Path.cwd(),'osnBridge_configs')
            if (not self.config_dir.exists()):
                self.config_dir.mkdir()
            for i in range(num_nodes):
                template["apps"]["org.onosproject.osnBridge"]["osnBridge_service"]\
                    ["socialConfig"]["CLOSocialId"] = base_user+str(i)+"@"+server
                template["apps"]["org.onosproject.osnBridge"]["osnBridge_service"]\
                    ["socialConfig"]["CLOSocialPassword"] = base_user+str(i)
                template["apps"]["org.onosproject.osnBridge"]["osnBridge_service"]\
                    ["socialConfig"]["CLOSocialServer"] = server
                template["apps"]["org.onosproject.osnBridge"]["osnBridge_service"] \
                    ["socialConfig"]["PLOSocialId"] = "I" + base_user + str(i) + "@" + server
                self.generate_json(template, file_name="osnBridge_config_" + str(i) + ".json")
        else:
            print("check template json file paths, could not find a valid path.")

    def create_dns_config(self, kwargs):
        base_file = kwargs["base_file"]
        base_user = kwargs["base_user"]
        server = kwargs["server"]
        num_nodes = int(kwargs["num_nodes"])
        if (Path(base_file).exists() and num_nodes != None):
            with open(base_file) as template_file:
                try:
                    template = json.load(template_file)
                except:
                    print("malformed json file {}".format(template))
                    exit()
            self.config_dir = Path(Path.cwd(), 'dns_configs')
            if (not self.config_dir.exists()):
                self.config_dir.mkdir()
            for i in range(num_nodes):
                template["username"] = "I" +base_user + str(i) + "@" + server
                template["password"] = "I" + base_user + str(i)
                template["server"] = server
                template["gateway"] = base_user + str(i) + "@" + server
                self.generate_json(template, file_name="dns_config_" + str(i) + ".json")
        else:
            print("check template json file paths, could not find a valid path.")



if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", dest="social", help="social account template")
    parser.add_argument("-r", dest="resources", help="static resource template")
    parser.add_argument("-i", dest="ipop", help="ipop base configuration")
    parser.add_argument("-g", dest="generic", help="generic configuration")
    parser.add_argument("-rem", dest="remote", help="generate")

    args = parser.parse_args()
    if (args.social != None  and args.resources != None):
        cf = configurationFactory(type = "social", social_template_file = args.social, resource_template_file = args.resources)
        cf.create_social_config()
        cf.create_static_resources()
    elif (args.ipop != None):
        cf = configurationFactory(type = "ipop", ipop_base_file_path = args.ipop, base_username="perso_", num_configs = 7 )
    elif (args.generic != None):
        cf = configurationFactory(type = "generic", template_path = args.generic)
    elif (args.remote != None):
        cf = configurationFactory(type = "remote", remoteinfo_config = args.remote)