from configparser import RawConfigParser
from pathlib import Path

class PoolConfig:
    def __init__(self):
        self.home = str(Path.home())
        env_path = self.home+'/core3-tbw/core/config/pool_config.ini'

        config = RawConfigParser()
        if (len(config.read(env_path)) == 0):
            self.error = True
        else:
            self.error = False
            self.pool(config)
        
    def pool(self, c):
        self.pool_ip = c.get('pool', 'pool_ip', fallback="127.0.0.1")
        self.pool_port = c.get('pool', 'pool_port', fallback="5000")
        self.pool_template = c.get('pool', 'pool_template', fallback="osrn")
        self.explorer = c.get('pool', 'explorer', fallback="https://testnet.explore.solar")
        self.coin = c.get('pool', 'coin', fallback="DSXP")
        self.proposal1 = c.get('pool', 'proposal1', fallback="https://delegates.solar.org/delegates/xxxx")
        self.proposal2 = c.get('pool', 'proposal2', fallback="https://yy.yy.yy/")
        self.proposal2_lang = c.get('pool', 'proposal2_lang', fallback="LANG")
        
