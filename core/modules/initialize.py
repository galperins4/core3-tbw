import os
from pathlib import Path

class Initialize:
    def __init__(self, database, sql):
        self.home = str(Path.home())
        self.database = database
        data_path = self.home+'/core3-tbw/core/data/tbw.db'
        
        if os.path.exists(data_path) == False:
            print("Setting up database")
            quit()
            self.initialize()
            print("Finished setting up database")
            quit()
            
        else:
            print("Database detected - no initialization needed")
    
    def initialize(self):
        pass

    
    
