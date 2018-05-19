import json
import subprocess
import argparse


def create_accounts(domain, username, password):
    cmd = "ejabberdctl register {} {} {}".format(username, domain, password)
    print(cmd)



def forge_relations(user1,user2,domain):
    cmd1 = "ejabberdctl add-rosteritem {} {} {} {} {}-{} groupvpn both"\
            .format(user1,domain,user2,domain,user1,user2)
    cmd2 = "ejabberdctl add-rosteritem {} {} {} {} {}-{} groupvpn both" \
        .format(user2, domain, user1, domain, user2, user1)
    print("\n")
    print(cmd1)
    print(cmd2)
    subprocess.call(cmd1,shell=True)
    subprocess.call(cmd2,shell=True)

def create_all_to_all(data):
    domain = data["domain"]
    leading_id = data["leading_id"]
    num_nodes = data["num_nodes"]
    social_ids = []
    for i in range(num_nodes):
        social_ids.append(leading_id+str(i))
        create_accounts(domain, social_ids[i], social_ids[i])
    for  i in range(len(social_ids)):
        for j in range(i+1,len(social_ids)):
            forge_relations(social_ids[i], social_ids[j], domain)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", dest="custom", help="custom social graph")
    parser.add_argument("-a", dest="alltoall", help="create all to all social relationships")
    args = parser.parse_args()
    if (args.custom != None):
        with open(args.custom) as json_file:
            data = json.load(json_file)
            domain = data["domain"]
            for node in data['relations']:
                create_accounts(domain, node, node)
            for node in data["relations"]:
                friends = data["relations"][node]
                for friend in friends:
                    forge_relations(node,friend,domain)
    elif (args.alltoall != None):
        with open(args.alltoall) as json_file:
            data = json.load(json_file)
            create_all_to_all(data)
    else:
        print("No arguments were specified")