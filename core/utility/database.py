import psycopg


class Database:
    def __init__(self, config, network):
        self.database = network.database
        self.username = config.username
        self.password = network.password
        self.delegate = config.delegate
        self.publickey = self.get_publickey()
       
    
    
    def open_connection(self):
        self.connection = psycopg.connect(
            dbname = self.database,
            user = self.username,
            password= self.password,
            host='localhost',
            port='5432')
            
        self.cursor=self.connection.cursor()
    
    '''
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
    '''    
        
    def get_publickey(self):
        try:
            universe = self.cursor.execute(f"""SELECT "sender_public_key", "asset" FROM transactions WHERE 
            "type" = 2""").fetchall()
            # universe = self.cursor.fetchall()
        except Exception as e:
            print(e)
    
        for i in universe:
            for k,v in i[1].items():
                if k == 'delegate' and v['username']==self.delegate:
                    self.publickey = i[0]
    
# BLOCK OPERATIONS    
    def get_all_blocks(self):
        try:
            return self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height" FROM blocks WHERE "generator_public_key" = '{self.publickey}' 
            ORDER BY "height" DESC""").fetchall()
            # return self.cursor.fetchall()
        except Exception as e:
            print(e)
    
    
    def get_limit_blocks(self):
        try:
            return self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height" FROM blocks WHERE "generator_public_key" = '{self.publickey}' 
            ORDER BY "height" DESC LIMIT 500""").fetchall()
            # return self.cursor.fetchall()
        except Exception as e:
            print(e)
            

# VOTE OPERATIONS
    def get_votes(self, timestamp):
        try:
            v = "+" + self.publickey
            u = "-" + self.publickey

            # get all votes
            vote = self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = 3) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % (timestamp, v)).fetchall()

            # vote = self.cursor.fetchall()

            #get all unvotes
            unvote = self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = 3) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % (timestamp, u)).fetchall()
        
            # unvote = cursor.fetchall()
            return vote, unvote
        except Exception as e:
            print(e)


# ACCOUNT OPERATIONS
    
