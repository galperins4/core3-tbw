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
            self.database.open_connection()
            total_blocks = self.database.get_all_blocks()
            self.database.close_connection()
            
            print("Storing forged blocks in database")
            self.sql.open_connection()
            self.sql.store_blocks(total_blocks)
            
            print("Marking blocks proccessed up to starting block")
            self.sql.mark_processed(self.config.start_block, initial = "Y")
            self.sql.close_connection()
            
            print("Finished setting up database")
            
        else:
            print("Database detected - no initialization needed")
    
    def initialize(self):
        self.sql.open_connection()
        self.sql.setup()
        self.sql.close_connection()
        quit()

    
    
