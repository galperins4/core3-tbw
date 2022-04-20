from configparser import SafeConfigParser
from pathlib import Path
import os


class Network:
    def __init__(self, network):
        self.home = str(Path.home())
        self.network = network
        env_path = self.home + "/core3-tbw/core/network/" + self.network

        config = SafeConfigParser(os.environ)
        config.read(env_path)
        self.load_network(config)

    def load_network(self, c):
        self.epoch = c.get("network", "epoch").split(",")
        self.version = int(c.get("network", "version"))
        self.wif = int(c.get("network", "wif"))
        self.api = int(c.get("network", "api"))
        self.database = c.get("network", "database")
        self.database_host = c.get("network", "database_host", fallback="127.0.0.1")
        self.user = c.get("network", "user")
        self.password = c.get("network", "password")
