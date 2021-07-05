import psycopg2


class Database:
    def __init__(self, config, network):
        self.database = network.database
        self.username = config.username
        self.password = network.password
    
    
    def open_connection(self):
        self.connection = psycopg2.connect(
            dbname = self.database,
            user = self.username,
            password= self.password,
            host='localhost',
            port='5432')
            
        self.cursor=self.connection.cursor()
    
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        
        
    def get_publickey(self):
        try:
            self.cursor.execute(f"""SELECT "sender_public_key", "asset" FROM transactions WHERE "type" = 2""")
            universe = self.cursor.fetchall()
        except Exception as e:
            print(e)
    
        for i in universe:
            for k,v in i[1].items():
                if k == 'delegate' and v['username']=='genesis_1':
                    self.publickey = i[0]
    
    def get_current_nonce(self):
        pass
    
    
    def get_blocks(self):
        pass
    
        
