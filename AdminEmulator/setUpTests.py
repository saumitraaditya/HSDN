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
    args = parser.parse_args()
    cf = configurationFactory(args.social, args.resources)
    cf.create_social_config()
    cf.create_static_resources()