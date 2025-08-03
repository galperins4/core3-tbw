from client import ArkClient
#from crypto.configuration.network import set_custom_network
from crypto.configuration.network import Network
import datetime


class Utility:
    def __init__(self, network):
        net = Network()
        self.network = network
        crypto_net = network.network.partition("_")[2]
        if crypto_net == "testnet":
            net.set_network(net.get_network())
        #self.build_network()
    
    
    def get_client(self, ip="localhost"):
        return ArkClient('http://{0}:{1}/api'.format(ip, self.network.api))

    def get_pool_client(self, ip="localhost"):
        return ArkClient('http://{0}:{1}/api'.format(ip, self.network.tx_api))

    
    def build_network(self):
        t = [int(i) for i in self.network.epoch]
        epoch = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5])
        set_custom_network(epoch, self.network.version, self.network.wif)
