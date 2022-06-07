from client import ArkClient
from crypto.configuration.network import set_custom_network
import datetime


class Utility:
    def __init__(self, network):
        self.network = network
        self.build_network()
    
    
    def get_client(self, ip="localhost"):
        return ArkClient('http://{0}:{1}/api'.format(ip, self.network.api))
    
    
    def build_network(self):
        t = [int(i) for i in self.network.epoch]
        epoch = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5])
        set_custom_network(epoch, self.network.version, self.network.wif)
