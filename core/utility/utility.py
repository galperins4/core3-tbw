from client import ArkClient


class Utility:
    def __init__(self, network):
        self.network = network
    
    
    def get_client(self, ip="localhost"):
        return ArkClient('http://{0}:{1}/api'.format(ip, self.network.api))
