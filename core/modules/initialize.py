import os
from pathlib import Path

class Initialize:
    def __init__(self, config, database, sql):
        self.home = str(Path.home())
        self.database = database
        self.sql = sql
        self.config = config
        data_path = self.home+'/core3-tbw/core/data/tbw.db'
        
        if os.path.exists(data_path) == False:
            print("Setting up database")
            self.initialize()
            
            print("Importing forged blocks")
            
            
            print("Storing forged blocks in database")
            
            
            print("Marking blocks proccessed up to starting block")
            
            
            print("Finished setting up database")
            
        else:
            print("Database detected - no initialization needed")
    
    def initialize(self):
        self.sql.open_connection()
        self.sql.setup()
        self.sql.close_connection()
        quit()

    
    
