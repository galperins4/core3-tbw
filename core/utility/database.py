import psycopg
import logging
from solar_crypto.constants import *

class Database:
    def __init__(self, config, network):
        self.logger = logging.getLogger(__name__)
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
            "type_group" = {TRANSACTION_TYPE_GROUP.CORE.value} AND "type" = {TRANSACTION_DELEGATE_REGISTRATION}""").fetchall()
        except Exception as e:
            self.logger.error(e)
    
        for i in universe:
            for k,v in i[1].items():
                if k == 'delegate' and v['username']==self.delegate:
                    self.publickey = i[0]
    
# BLOCK OPERATIONS    
    def get_block_timestamp(self, block):
        try:
            return self.cursor.execute(f"""SELECT "timestamp" from blocks where "height" = {block}""").fetchall()
        except Exception as e:
            self.logger.error(e)
    
    
    def get_all_blocks(self):
        try:
            return self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height", "burned_fee", "donations" FROM blocks WHERE "generator_public_key" = '{self.publickey}' 
            ORDER BY "height" DESC""").fetchall()
        except Exception as e:
            self.logger.error(e)
    
    
    def get_limit_blocks(self, timestamp):
        try:
            return self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
            "height", "burned_fee", "donations" FROM blocks WHERE "generator_public_key" = '{self.publickey}' AND 
            "timestamp" > {timestamp} ORDER BY "height" """).fetchall()
        except Exception as e:
            self.logger.error(e)
            

# VOTE OPERATIONS
    def get_last_multivote(self, account, timestamp):
        try:
            output = self.cursor.execute(f"""SELECT "timestamp" from "transactions" WHERE "timestamp" <= {timestamp} 
            AND  "type_group" = {TRANSACTION_TYPE_GROUP.SOLAR.value} and "type" = {SOLAR_TRANSACTION_VOTE} AND "sender_public_key" = '{account}' ORDER BY
            "timestamp" DESC LIMIT 1 """).fetchall()
        except Exception as e:
            self.logger.error(e)

        if len(output) == 0:
            output = None
        else: 
            output = output[0][0]

        return output


    def get_multivotes(self, timestamp):
        try:
            return self.cursor.execute("""
            SELECT DISTINCT ON (1) "sender_public_key", "timestamp", "asset"->'votes'->'%s' AS "percent"
            FROM (
                  SELECT * FROM "transactions"
                  WHERE "timestamp" <= %s
                  AND "type_group" = %s
                  AND "type" = %s
                 )
            AS "filtered" WHERE asset->'votes'->'%s' IS NOT NULL ORDER BY 1,2 DESC,3;
            """ % (self.delegate, timestamp, TRANSACTION_TYPE_GROUP.SOLAR.value, SOLAR_TRANSACTION_VOTE, self.delegate)).fetchall()
        except Exception as e:
            self.logger.error(e)

    
    def get_votes(self, timestamp):
        try:
            v = "+" + self.publickey
            u = "-" + self.publickey
            vd = "+" + self.delegate
            ud = "-" + self.delegate
            
            # get all votes
            vote = self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp", 100 FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = %s AND "type_group" = %s) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb OR asset::jsonb @> '{"votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % 
            (timestamp, TRANSACTION_VOTE, TRANSACTION_TYPE_GROUP.CORE.value, v, vd)).fetchall()

            #get all unvotes
            unvote = self.cursor.execute("""SELECT "sender_public_key", MAX("timestamp") AS "timestamp", 100 FROM (SELECT * FROM 
            "transactions" WHERE "timestamp" <= %s AND "type" = %s AND "type_group" = %s) AS "filtered" WHERE asset::jsonb @> '{
            "votes": ["%s"]}'::jsonb OR asset::jsonb @> '{"votes": ["%s"]}'::jsonb GROUP BY "sender_public_key";""" % 
            (timestamp, TRANSACTION_VOTE, TRANSACTION_TYPE_GROUP.CORE.value, u, ud)).fetchall()

            return vote, unvote
        except Exception as e:
            self.logger.error(e)


    # ACCOUNT OPERATIONS
    def get_sum_inbound(self, account, timestamp, chkpoint_timestamp):
        non_multi_htlc = 0
        htlc = 0
        multi = 0
        # get inbound transactions (non-multi, non-htlc)
        try:
            # note: type_group NOT specified on purpose
            output = self.cursor.execute(f''' SELECT SUM("amount") FROM (
                                                SELECT * FROM "transactions" 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND "recipient_id" = '{account}' 
                                                  AND "type" NOT IN ({TRANSACTION_TRANSFER}, {TRANSACTION_HTLC_LOCK}, {TRANSACTION_HTLC_CLAIM}, {TRANSACTION_HTLC_REFUND})
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                non_multi_htlc = int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # get inbound transactions (htlc-claimed)
        try:
            output = self.cursor.execute(f''' SELECT SUM("amount") FROM (
                                                SELECT * FROM "transactions" 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND "recipient_id" = '{account}' 
                                                  AND "type_group" = {TRANSACTION_TYPE_GROUP.CORE.value}
                                                  AND "type" = {TRANSACTION_HTLC_LOCK}
                                                  AND id IN (SELECT asset ->'claim'->>'lockTransactionId' from "transactions" where type={TRANSACTION_HTLC_CLAIM})
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                htlc =  int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # get inbound transactions (transfers)
        try:
            output = self.cursor.execute(f''' SELECT SUM("amount") FROM (
                                                SELECT id, block_height, x.amount, x."recipientId" FROM "transactions", jsonb_to_recordset(asset->'transfers') AS x(amount bigint, "recipientId" text) 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND x."recipientId" = '{account}' 
                                                  AND "type_group" = {TRANSACTION_TYPE_GROUP.CORE.value}
                                                  AND "type" = {TRANSACTION_TRANSFER}
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                multi = int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # sum up
        total = non_multi_htlc + htlc + multi
        self.logger.debug(f""" .. incoming tx <- non_multi_htlc:{non_multi_htlc} + htlc:{htlc} + multi:{multi} = total:{total}""")
        return total


    def get_sum_outbound(self, account, timestamp, chkpoint_timestamp):
        non_multi_htlc = 0
        htlc = 0
        multi = 0
        txfees = 0
        # get outbound transactions (non-multi, non-htlc)
        try:
            # note: type_group NOT specified on purpose
            output = self.cursor.execute(f''' SELECT SUM("amount") FROM (
                                                SELECT * FROM "transactions" 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND "sender_id" = '{account}' 
                                                  AND "type" NOT IN ({TRANSACTION_TRANSFER}, {TRANSACTION_HTLC_LOCK}, {TRANSACTION_HTLC_CLAIM}, {TRANSACTION_HTLC_REFUND})
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                non_multi_htlc = int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # get outbound transactions (htlc-claimed)
        try:
            output = self.cursor.execute(f''' SELECT SUM("amount") FROM (
                                                SELECT * FROM "transactions" 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND "sender_id" = '{account}' 
                                                  AND "type_group" = {TRANSACTION_TYPE_GROUP.CORE.value}
                                                  AND "type" = {TRANSACTION_HTLC_LOCK}
                                                  AND id IN (SELECT asset ->'claim'->>'lockTransactionId' from "transactions" where type={TRANSACTION_HTLC_CLAIM})
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                htlc =  int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # get outbound transactions (transfer)
        try:
            output = self.cursor.execute(f''' SELECT SUM("amount") FROM (
                                                SELECT id, block_height, x.amount, x."recipientId" FROM "transactions", jsonb_to_recordset(asset->'transfers') AS x(amount bigint, "recipientId" text) 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND "sender_id" = '{account}' 
                                                  AND "type_group" = {TRANSACTION_TYPE_GROUP.CORE.value}
                                                  AND "type" = {TRANSACTION_TRANSFER}
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                multi = int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # get all outbound transaction fees
        try:
            output = self.cursor.execute(f''' SELECT SUM("fee") FROM (
                                                SELECT * FROM "transactions" 
                                                WHERE "timestamp" <= {timestamp}
                                                  AND "timestamp" > {chkpoint_timestamp}
                                                  AND "sender_id" = '{account}' 
                                              ) AS "filtered"''').fetchall()
            if output[0][0] != None:
                txfees = int(output[0][0])
        except Exception as e:
            self.logger.error(e)

        # sum up
        total = non_multi_htlc + htlc + multi + txfees
        self.logger.debug(f""" .  outgoing tx -> non_multi_htlc:{non_multi_htlc} + htlc:{htlc} + multi:{multi} + txfees:{txfees} = total:{total}""")
        return total

            
    def get_sum_block_rewards(self, account, timestamp, chkpoint_timestamp):
        try:
            output = self.cursor.execute(f"""SELECT SUM("reward") AS "reward", SUM("total_fee") - SUM("burned_fee") AS "fee" FROM (SELECT * FROM "blocks"
            WHERE "timestamp" <= {timestamp} AND "timestamp" > {chkpoint_timestamp}) AS "filtered" WHERE "generator_public_key" = '{account}'""").fetchall()
            if output[0][0] == None:
                block_rewards = [0,0]
            else:
                block_rewards = [int(i) for i in output[0]]

            # Dev fund
            output = self.cursor.execute(f"""SELECT SUM(val) FROM ( SELECT SUM(value::numeric) val FROM blocks, jsonb_each_text(dev_fund) WHERE 
            "timestamp" <= {timestamp} AND "timestamp" > {chkpoint_timestamp} AND "generator_public_key" = '{account}' ) AS "filtered" """).fetchall()

            if output[0][0] != None:
                return (sum(block_rewards) - int(output[0][0]))
            
            return sum(block_rewards)
        except Exception as e:
            self.logger.error(e)
