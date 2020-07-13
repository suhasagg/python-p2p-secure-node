import json
import hashlib
import sqlite3
from datetime import time, date, datetime

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_Cipher
from Crypto.Signature import PKCS1_v1_5 as PKCS1_v1_5_Signature
from Crypto.Hash import SHA512
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
from base64 import b64decode, b64encode

from p2pnetwork.node import Node

"""
Author : Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.1 beta (use at your own risk!)

Python package p2psecure for implementing secure decentralized peer-to-peer network applications based
on the package p2pnetwork that provides a framework to create decentralized peer-to-peer network
applications with.
"""

class Blockchain:
    """This class implements the functionality of an immutable blockchain. You can store anything in the
    blockchain datastructure. But ... note ... you cannot delete anything when you pushed it on the block-
    chain. Summary of what a blockchain is! A blockchain is a ledger that creates and changes records of 
    the status of objects. A big administration to have the single source of truth. When sharing this ledger
    the nodes have the possiblity to determine the truth. Bitcoin is also build on a blockchain that uses
    the prove of work (requiring a lot of computing power, hence electrical power). To fix this blockchain
    you can implement your own scheme. Before a record can be added, you need to check it, otherwise your
    blockchain will simple not be good."""

    # Python class constructor
    def __init__(self):
        """Create instance of a Blockchain."""
        super(Blockchain, self).__init__()

        """The database that contains the blockchain."""
        self.db = sqlite3.connect('blockchain.db')
        self.init_database()
        
    def init_database(self):
        c = self.db.cursor()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='blockchain'")
        if ( c.fetchone()[0] != 1 ):
            c.execute("""CREATE TABLE blockchain(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       prev_hash TEXT,
                       type TEXT,
                       timestamp TEXT,
                       data TEXT,
                       nonce TEXT, 
                       hash TEXT)""")

    def add_block(self, block):
        """This method adds a block to the blockchain. It checks whether the hashes are correct of the block
           and of the previous block before it is added."""
        c = self.db.cursor()
        c.execute("INSERT INTO blockchain (prev_hash, type, timestamp, data, nonce, hash) VALUES (?, ?, ?, ?, ?, ?)",
                  ( block["prev_hash"],
                    block["type"], 
                    block["timestamp"],
                    json.dumps(block["data"], sort_keys=True),
                    block["nonce"],
                    block["hash"] ))
        self.db.commit()

    def get_blockchain_record(self, data):
        #(4, '0', 'transaction', '2020-07-12T21:53:22.549666', b'{"data": "MAurice Snoeren"}', '471497', '00000ce82c08eea5566b480fd00bb6d79bfd072a1dbabdeae345edd58554d254ebfce1776804ae862eec2c3726d4ae2b48845537fa64ddba79d5cde961686bd3')
        return {
            "id": int(data[0]),
            "prev_hash": data[1],
            "type": data[2],
            "timestamp": data[3], # CONVERT to date => datetime.strptime(data[3], "%Y-%m-%dT%H:%M:%S.%f"),
            "data": json.loads(data[4]),
            "nonce": data[5],
            "hash": data[6]
        }
        
    def get_block(self, index):
        """This method returns the block on the given index. When the index does not exist, None is returned."""
        pass
    
    def get_last_block(self):
        """This method returns the last block of the blockchain."""
        c = self.db.cursor()
        for row in c.execute('SELECT * FROM blockchain ORDER BY id DESC LIMIT 1'):
            return self.get_blockchain_record(row)
        return None

    def get_last_block_id(self):
        """This method returns the last block of the blockchain."""
        pass

    def process_block(self, data, type):
        """This method creates a new block to be inserted on the blockchain. It utilized proof-of-work or
           other interested algoritms to make the blockchain immutable and unhackable. To improve the chain,
           blocks needs to be added constantly."""
        last_block = self.get_last_block()
        print("LAST:")
        print(last_block)
        timestamp = datetime.now()
        block = {
            "id"       : (last_block["id"] + 1) if last_block != None else 1,
            "prev_hash": last_block["hash"] if last_block != None else 0,
            "type"     : type,
            "timestamp": timestamp.isoformat(),
            "data"     : data,
            "nonce"    : 0
        }

        # Implementation of proof-of-work
        difficulty = 5
        h = hashlib.sha512()
        h.update( json.dumps(block, sort_keys=True).encode("utf-8") )
        while ( h.hexdigest()[:difficulty] != "0"*difficulty ):
            block["nonce"] = block["nonce"] + 1
            h.update( json.dumps(block, sort_keys=True).encode("utf-8") )

        block["hash"] = h.hexdigest()
        print(block)
        return block
