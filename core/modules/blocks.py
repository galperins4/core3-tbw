class Blocks:
    def __init__(self, config, database, sql):
        self.database = database
        self.sql = sql
        self.config = config
        
    
    def get_last_block(self):
        self.sql.open_connection()
        last_block = self.sql.last_block().fetchall()
        self.sql.close_connection()
        return last_block
        
        
    def get_new_blocks(self, last_block):
        self.database.open_connection()
        new_blocks = self.database.get_limit_blocks(last_block[0][0])
        self.database.close_connection()
        return new_blocks
        
        
    def store_new_blocks(self, new_blocks):
        self.sql.open_connection()
        self.sql.store_blocks(new_blocks)
        self.sql.close_connection()
        
        
    def return_unprocessed_blocks(self):
        self.sql.open_connection()
        unprocessed_blocks = self.sql.unprocessed_blocks().fetchall()
        self.sql.close_connection()
        return unprocessed_blocks
    
    
    def block_counter(self):
        self.sql.open_connection()
        processed_blocks = self.sql.processed_blocks().fetchall()
        self.sql.close_connection()
        return len(processed_blocks)
       
