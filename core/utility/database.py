import psycopg2


class Database:
    def __init__(self, config, network):
        self.database = network.database
        self.username = config.username
        self.password = network.password
        self.delegate = config.delegate
        
        self.open_connection()
        self.get_publickey()
        self.close_connection()
    
    
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
                if k == 'delegate' and v['username']==self.delegate:
                    self.publickey = i[0]
    
# BLOCK OPERATIONS    
    def get_all_blocks(self):
        try:
            self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height" FROM blocks WHERE "generator_public_key" = '{self.publickey}' ORDER BY "height" DESC""")
            return self.cursor.fetchall()
        except Exception as e:
            print(e)
    
    
    def get_limit_blocks(self):
        try:
            self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height" FROM blocks WHERE "generator_public_key" = '{self.publickey}' ORDER BY "height" DESC LIMIT 250""")
            return self.cursor.fetchall()
        except Exception as e:
            print(e)
            

# VOTE OPERATIONS
    def get_votes(self, timestamp):
        try:
            v = "+" + self.publickey
            u = "-" + self.publickey

            # get all votes
            self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = 3) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % (timestamp, v))

            vote = self.cursor.fetchall()

            #get all unvotes
            self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = 3) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % (timestamp, u))
        
            unvote = cursor.fetchall()
            return vote, unvote
        except Exception as e:
            print(e)








# ACCOUNT OPERATIONS
    
