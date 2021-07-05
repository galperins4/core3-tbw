import os
from pathlib import Path

class Initialize:
    def __init__(self):
        self.home = str(Path.home())
        data_path = self.home+'/core3-tbw/core/data/tbw.db'
        
        if os.path.exists(data_path) == False:
            print("Setting up database")
            self.initialize()
            print("Finished setting up database")
            quit()
            
        else:
            print("Database detected - no initialization needed")
    
    def initialize(self):
        pass

    
    
