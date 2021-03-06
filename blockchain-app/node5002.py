import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse 

# Building Blockchain
class Blockcahin:
    ''' Main class of blockchain '''
    def __init__(self):
        self.chain = []
        self.transactions = [] 
        self.create_block(proof=1, prev_hash='0')
        self.nodes = set()

    def create_block(self, proof, prev_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        


# Mining Blockchain
app = Flask(__name__)

# Create address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

blockchain = Blockcahin()

# Mine a block
@app.route('/mine_block', methods=['GET',])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transaction(sender=node_address, receiver='Emily', amount=1)
    new_block = blockchain.create_block(proof=proof, prev_hash=prev_hash)
    
    response = {
        'message': 'Block mined successfully!',
        'block': new_block,
    }
    return jsonify(response), 200


# Get full blockchain
@app.route('/get_chain', methods=['GET',])
def get_chain():
    resoponse = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(resoponse), 200


@app.route('/is_valid', methods=['GET',])
def is_valid():
    response = {
        'chain': blockchain.chain,
        'is_valid': blockchain.is_chain_valid(blockchain.chain)
    }
    return jsonify(response), 200

# Adding a new transaction to the blockchain
@app.route('/add_transaction', methods=['POST',])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount',]
    if not all (key in json for key in transaction_keys):
        return 'Missing keys in request', 400
    index = blockchain.add_transaction(sender=json['sender'], receiver=json['receiver'], amount=json['amount'] )
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201

# Decentralizing the blockchain
@app.route('/connect_node', methods=['POST',])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': f'Connected {len(nodes)} nodes', 'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET',])
def replace_chain():
    chain_replaced = blockchain.replace_chain()
    response = {
        'chain_replaced': chain_replaced,
        'chain': blockchain.chain
    }
    return jsonify(response), 200

# Run App
app.run(host='0.0.0.0', port='5002')