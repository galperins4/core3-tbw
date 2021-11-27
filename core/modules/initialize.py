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
            self.initialize()
            quit()
        else:
            print("Database detected - no initialization needed")

        self.update_delegate_records()
    
    def initialize(self):
        self.sql.open_connection()
        
        print("Setting up database")
        self.sql.setup()
        
        print("Importing forged blocks")
        self.database.open_connection()
        total_blocks = self.database.get_all_blocks()
        self.database.close_connection()
            
        print("Storing forged blocks in database")
        self.sql.store_blocks(total_blocks)
            
        print("Marking blocks proccessed up to starting block {}".format(self.config.start_block))
        self.sql.mark_processed(self.config.start_block, initial = "Y")
        processed_blocks = self.sql.processed_blocks().fetchall()
        self.sql.close_connection()
            
        print("Total blocks imported - {}".format(len(total_blocks)))
        print("Total blocks marked as processed - {}".format(len(processed_blocks)))
        print("Finished setting up database")

    
    def update_delegate_records(self):
        self.sql.open_connection()
        accounts = [i for i in self.config.delegate_fee_address]
        self.sql.store_delegate_rewards(accounts)
        self.sql.close_connection()
