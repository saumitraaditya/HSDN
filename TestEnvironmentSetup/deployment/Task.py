from layered_policy import LayeredPolicy
import time
class Task:

    '''
    needs to keep track of devices that have been volunteered by
    users and than will have to figure out a topology based on a policy
    '''
    def __init__(self,template):
        self.description = template
        self.policy = None
        self.initiation_time = time.time()
        self.links_requested = {}
        self.total_links_requested = 0
        self.total_links_established = 0

    def configure_network_policy(self,*args):
        '''assumes hardcoded layered policy for testing and prototyping'''
        self.policy = LayeredPolicy(args[0], args[1], args[2])
