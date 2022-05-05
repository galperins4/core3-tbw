import sqlite3
from datetime import datetime
from pathlib import Path

class Sql:
    def __init__(self):
        self.home = str(Path.home())
        self.data_path = self.home+'/core3-tbw/core/data/tbw.db'

        
    def open_connection(self):
        self.connection = sqlite3.connect(self.data_path)
        self.cursor = self.connection.cursor()
    
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
    
    
    def commit(self):
        return self.connection.commit()


    def execute(self, query, args=[]):
        return self.cursor.execute(query, args)


    def executemany(self, query, args):
        return self.cursor.executemany(query, args)


    def fetchone(self):
        return self.cursor.fetchone()


    def fetchall(self):
        return self.cursor.fetchall()


    def setup(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS blocks (id varchar(64) PRIMARY KEY, timestamp int, reward int, totalFee bigint, height int, processed_at varchar(64) null)")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS voters (address varchar(36) PRIMARY KEY, public_key varchar(66), unpaid_bal bigint, paid_bal bigint, share float )")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS transactions (address varchar(36), amount varchar(64), id varchar(64), processed_at varchar(64) )")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS delegate_rewards (address varchar(36), unpaid_bal bigint, paid_bal bigint )")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS staging (address varchar(36), payamt bigint, msg varchar(64), processed_at varchar(64) null )")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS exchange (initial_address varchar(36), payin_address varchar(36), exchange_address varchar(64), payamt bigint, exchangeid varchar(64), processed_at varchar(64) null )")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS voters_balance_checkpoint (address varchar(36) PRIMARY KEY, balance bigint, timestamp int )")

        self.connection.commit()


    def store_exchange(self, i_address, pay_address, e_address, amount, exchangeid):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exchange=[]
        exchange.append((i_address, pay_address, e_address, amount, exchangeid, ts))
        self.executemany("INSERT INTO exchange VALUES (?,?,?,?,?,?)", exchange)
        self.commit()
    
    
    def stage_payment(self, paid, msg):
        staging = []
        for k, v in paid.items():
            staging.append((k, v, msg, None))

        self.executemany("INSERT INTO staging VALUES (?,?,?,?)", staging)
        self.commit()


    def store_blocks(self, blocks):
        newBlocks=[]

        for block in blocks:
            self.cursor.execute("SELECT id FROM blocks WHERE id = ?", (block[0],))

            if self.cursor.fetchone() is None:
                newBlocks.append((block[0], block[1], block[2], block[3], block[4], None))

        self.executemany("INSERT INTO blocks VALUES (?,?,?,?,?,?)", newBlocks)

        self.commit()

    def store_voters(self, voters, share):
        newVoters=[]

        for voter in voters:
            self.cursor.execute("SELECT address FROM voters WHERE address = ?", (voter[0],))

            if self.cursor.fetchone() is None:
                newVoters.append((voter[0], voter[1], 0, 0, share))

        self.executemany("INSERT INTO voters VALUES (?,?,?,?,?)", newVoters)

        self.commit()


    def store_delegate_rewards(self, delegate):
        newRewards=[]

        for d in delegate:
            self.cursor.execute("SELECT address FROM delegate_rewards WHERE address = ?", (d,))

            if self.cursor.fetchone() is None:
                newRewards.append((d, 0, 0))

        self.executemany("INSERT INTO delegate_rewards VALUES (?,?,?)", newRewards)

        self.commit()


    def store_transactions(self, tx):
        newTransactions=[]
        
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for t in tx:
            self.cursor.execute("SELECT id FROM transactions WHERE id = ?", (t[2],))
            
            if self.cursor.fetchone() is None:
                newTransactions.append((t[0], t[1], t[2], ts))
                
        self.executemany("INSERT INTO transactions VALUES (?,?,?,?)", newTransactions)
        
        self.commit()


    def mark_processed(self, block, initial="N"):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if initial == "N":
            self.cursor.execute(f"UPDATE blocks SET processed_at = '{ts}' WHERE height = '{block}'")
        else:
            self.cursor.execute(f"UPDATE blocks SET processed_at = '{ts}' WHERE height <= '{block}'")
        
        self.commit()


    def blocks(self):
        return self.cursor.execute("SELECT * FROM blocks")


    def last_block(self): 
        return self.cursor.execute("SELECT timestamp, height from blocks ORDER BY height DESC LIMIT 1")
    
    
    def processed_blocks(self):
        return self.cursor.execute("SELECT * FROM blocks WHERE processed_at NOT NULL")


    def unprocessed_blocks(self):
        return self.cursor.execute("SELECT * FROM blocks WHERE processed_at IS NULL ORDER BY height")
    
    
    def unprocessed_staged_payments(self):
        return self.cursor.execute("SELECT COUNT(*) FROM staging WHERE processed_at is NULL").fetchall()[0][0]


    def get_staged_payment(self, lim=40, multi='N'):
        if multi == 'N':
            return self.cursor.execute(f"SELECT rowid, * FROM staging WHERE processed_at IS NULL LIMIT {lim}")
        else:
            return self.cursor.execute(f"SELECT rowid, * FROM staging WHERE processed_at IS NULL")
            

    def process_staged_payment(self, rows):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')		
        for i in rows:
            self.cursor.execute(f"UPDATE staging SET processed_at = '{ts}' WHERE rowid = {i}")
        self.commit()

    
    def delete_staged_payment(self):
        self.cursor.execute("DELETE FROM staging WHERE processed_at NOT NULL")     
        self.commit()

    
    def delete_test_exchange(self,p_in,p_out,amount):
        self.cursor.execute(f"DELETE FROM exchange WHERE initial_address = '{p_in}' AND payin_address = '{p_out}' AND payamt = '{amount}'")
        self.commit()
    
    
    def delete_transaction_record(self, txid):
        self.cursor.execute(f"DELETE FROM transactions WHERE id = '{txid}'")
        self.commit()

    
    def all_voters(self):
        return self.cursor.execute("SELECT * FROM voters ORDER BY unpaid_bal DESC")
    
    
    def voters(self):
        return self.cursor.execute("SELECT * FROM voters WHERE unpaid_bal > 0 ORDER BY unpaid_bal DESC")


    def rewards(self):
        return self.cursor.execute("SELECT * FROM delegate_rewards WHERE unpaid_bal > 0")


    def transactions(self):
        return self.cursor.execute("SELECT * FROM transactions ORDER BY processed_at DESC LIMIT 1000")

    
    def update_voter_balance(self, voter_unpaid):
        for k, v in voter_unpaid.items():
            self.cursor.execute(f"UPDATE voters SET unpaid_bal = unpaid_bal + {v} WHERE address = '{k}'")
            self.commit()


    def update_delegate_balance(self, delegate_unpaid):
        for k, v in delegate_unpaid.items():
            self.cursor.execute(f"UPDATE delegate_rewards SET unpaid_bal = unpaid_bal + {v} WHERE address = '{k}'")
            self.commit()


    def update_voter_paid_balance (self, paid):
        for k, v in paid.items():
            self.cursor.execute(f"UPDATE voters SET paid_bal = paid_bal + {v} WHERE address = '{k}'")
            self.cursor.execute(f"UPDATE voters SET unpaid_bal = unpaid_bal - {v} WHERE address = '{k}'")
            self.commit()


    def update_delegate_paid_balance (self, paid):
        for k,v in paid.items():
            self.cursor.execute(f"UPDATE delegate_rewards SET paid_bal = paid_bal + unpaid_bal WHERE address = '{k}'")
            self.cursor.execute(f"UPDATE delegate_rewards SET unpaid_bal = unpaid_bal - unpaid_bal WHERE address = '{k}'")
            self.commit()

    
    def update_voter_share(self, address, share):
        self.cursor.execute("UPDATE voters SET share = {0} WHERE address = '{1}'".format(share, address))
        self.commit()


    def get_voter_share(self, address):
        return self.cursor.execute("SELECT share FROM voters WHERE address = '{0}'".format(address))

    
    def get_voter_balance_checkpoint(self, address):
        return self.cursor.execute(f"SELECT * FROM voters_balance_checkpoint WHERE address = '{address}'")
    
    
    def get_all_voters_balance_checkpoint(self):
        ts = self.cursor.execute("SELECT MAX(timestamp) FROM voters_balance_checkpoint").fetchall()[0][0]
        return self.cursor.execute(f"SELECT balance FROM voters_balance_checkpoint WHERE timestamp = {ts}")

    
    def update_voter_balance_checkpoint(self, vote_balance, block_timestamp):
        self.executemany("INSERT OR REPLACE INTO voters_balance_checkpoint(address,balance,timestamp) VALUES (?,?,?)", [(k,v,block_timestamp) for k,v in vote_balance.items()])
        self.commit()
