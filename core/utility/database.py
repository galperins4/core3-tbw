import psycopg


class Database:
    def __init__(self, config, network):
        self.database = network.database
        self.database_host = network.database_host
        self.username = config.username
        self.password = network.password
        self.delegate = config.delegate
        
        self.open_connection()
        self.get_publickey()
        self.close_connection()
       
    
    def open_connection(self):
        self.connection = psycopg.connect(
            dbname = self.database,
            user = self.username,
            password= self.password,
            host=self.database_host,
            port='5432')
            
        self.cursor=self.connection.cursor()
    
     
    def close_connection(self):
        self.cursor.close()
        self.connection.close() 
    
    
    def get_publickey(self):
        try:
            universe = self.cursor.execute(f"""SELECT "sender_public_key", "asset" FROM transactions WHERE 
            "type" = 2""").fetchall()
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
        except Exception as e:
            print(e)
    
    
    def get_limit_blocks(self, timestamp):
        try:
            return self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height" FROM blocks WHERE "generator_public_key" = '{self.publickey}' AND 
            "timestamp" > {timestamp} ORDER BY "height" """).fetchall()
        except Exception as e:
            print(e)
            

# VOTE OPERATIONS
    def get_votes(self, timestamp):
        try:
            v = "+" + self.publickey
            u = "-" + self.publickey

            # get all votes
            vote = self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = 3 AND "type_group" = 1) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % (timestamp, v)).fetchall()

            #get all unvotes
            unvote = self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = 3 AND "type_group" = 1) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % (timestamp, u)).fetchall()

            return vote, unvote
        except Exception as e:
            print(e)


    # ACCOUNT OPERATIONS
    def get_sum_inbound(self, account, timestamp, chkpoint_timestamp):
        try:
            # get inbound non-multi transactions
            output = self.cursor.execute(f"""SELECT SUM("amount") FROM (SELECT * FROM "transactions" WHERE "timestamp" <= {timestamp} AND "timestamp" > {chkpoint_timestamp}) AS
            "filtered" WHERE "recipient_id" = '{account}' AND "type" <> {6}""").fetchall()
            if output[0][0] == None:
                non_multi = [0]
            else:
                non_multi = [int(i) for i in output[0]]
        except Exception as e:
            print(e)

        try:
            # get inbound multi transactions
            multi_universe = self.cursor.execute("""SELECT "timestamp", "fee", "sender_public_key", "asset", "id" FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "timestamp" > %s) AS "filtered" WHERE asset::jsonb @> '{"payments": [{"recipientId":"%s"}]}'::jsonb;""" 
            % (timestamp, chkpoint_timestamp, account)).fetchall()
            # get amounts from multi transactions
            multi_amount = []
            for i in multi_universe:
                for j in i[3]['payments']:
                    if j['recipientId'] == account:
                        multi_amount.append(int(j['amount']))
        except Exception as e:
            print(e)
                        
        # append total non-multi to multi
        total = multi_amount + non_multi
        return sum(total)

            
    def get_sum_outbound(self, account, timestamp, chkpoint_timestamp):
        try:
            # Non multi transactions ( json asset is null )
            output = self.cursor.execute(f"""SELECT SUM("amount") as amount, SUM("fee") as fee FROM (SELECT * FROM "transactions" WHERE 
            "timestamp" <= {timestamp} AND "timestamp" > {chkpoint_timestamp}) AS "filtered" WHERE "sender_public_key" = '{account}' AND asset IS NULL""").fetchall()
            if output[0][0] == None:
                convert = [0,0]
            else:
                convert = [int(i) for i in output[0]]

            # votes + multi transactions ( json asset is not null )
            output = self.cursor.execute(f"""SELECT "fee" as fee, "asset" as asset FROM (SELECT * FROM "transactions" WHERE 
            "timestamp" <= {timestamp} AND "timestamp" > {chkpoint_timestamp}) AS "filtered" WHERE "sender_public_key" = '{account}' AND asset IS NOT NULL""").fetchall()
            if output:
                for transaction in output:
                    # fee
                    convert.append(int(transaction[0]))
                    # all payment in transaction
                    if 'payments' in transaction[1].keys():
                        for payment in transaction[1]['payments']:
                            convert.append(int(payment['amount']))
            return sum(convert)
        except Exception as e:
            print(e)
    
    
    def get_sum_block_rewards(self, account, timestamp, chkpoint_timestamp):
        try:
            output = self.cursor.execute(f"""SELECT SUM("reward") AS "reward", SUM("total_fee") AS "fee" FROM (SELECT * FROM "blocks" 
            WHERE "timestamp" <= {timestamp} AND "timestamp" > {chkpoint_timestamp}) AS "filtered" WHERE "generator_public_key" = '{account}'""").fetchall()
            if output[0][0] == None:
                block_rewards = [0,0]
            else:
                block_rewards = [int(i) for i in output[0]]
            return sum(block_rewards)
        except Exception as e:
            print(e)
