import psycopg2


class Database:
    def __init__(self, config, network):
        print(network.database)
        print(config.user)
        print(network.password)
    
    
    '''
    def __init__(self, db, u, pw, pk):
        self.db=db
        self.user=u
        self.password=pw
        self.PublicKey=pk
    
    
    def open_connection(self):
        self.connection = psycopg2.connect(
            dbname = self.db,
            user = self.user,
            password= self.password,
            host='localhost',
            port='5432')
            
        self.cursor=self.connection.cursor()
    
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
    '''
