import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse

class Blockchain:

    def __init__(self):
        """ Constructor de la clase. """

        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
      
    def create_block(self, proof, previous_hash):
        """ Creación de un nuevo bloque. 

        Arguments:
            - proof: Nounce del bloque actual.
            - previous_hash: Hash del bloque previo.

        Returns: 
            - block: Nuevo bloque creado. 
        """

        block = { 'index'         : len(self.chain)+1,
                'timestamp'     : str(datetime.datetime.now()),
                'proof'         : proof,
                'previous_hash' : previous_hash,
                'transactions'  : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        """ Obtención del bloque previo de la Blockchain.
        
        Returns:
            - Obtención del último bloque de la Blockchain. """

        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):     
        """ Protocolo de concenso Proof of Work (PoW).
        
        Arguments:
            - previous_proof: Nounce del bloque previo.

        Returns:
            - new_proof: Devolución del nuevo nounce obtenido con PoW. """

        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else: 
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        """ Cálculo del hash de un bloque.
        
        Arguments:
            - block: Identifica a un bloque de la Blockchain.
        
        Returns:
            - hash_block: Devuelve el hash del bloque """

        encoded_block = json.dumps(block, sort_keys = True).encode()
        hash_block = hashlib.sha256(encoded_block).hexdigest()
        return hash_block
    
    def is_chain_valid(self, chain):
        """ Determina si la Blockchain es válida. 
        
        Arguments:
            - chain: Cadena de bloques que contiene toda la 
                    información de las transacciones.
        
        Returns:
            - True/False: Devuelve un booleano en función de la validez de la 
                        Blockchain. (True = Válida, False = Inválida) """
                        
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        """ Realización de una transacción.
        
        Arguments:
            - sender: Persona que hace la transacción
            - receiver: Persona que recibe la transacción
            - amount: Cantidad de criptomonedas enviadas

        Returns: 
            - Devolución del índice superior al último bloque
        """

        self.transactions.append({'sender'  : sender,
                                'receiver': receiver, 
                                'amount'  : amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        """ Nuevo nodo en la Blockchain.
        
        Arguments:
            - address: Dirección del nuevo nodo
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        """ Remplazo de la cadena por la cadena más larga, 
        siempre y cuando sea válida. """
        
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