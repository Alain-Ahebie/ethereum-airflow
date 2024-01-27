import datetime
import pandas as pd
from web3 import Web3
from web3.exceptions import Web3Exception

def connect_to_ethereum_node(url):
    # Connects to an Ethereum node using the provided URL
    try:
        web3 = Web3(Web3.HTTPProvider(url))
        if not web3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum node")
        return print(f'Connected: {web3.is_connected()}')
    except Web3Exception as e:
        raise ConnectionError(f"An error occurred while connecting: {str(e)}")
    
INFURA_URL = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"   
connect_to_ethereum_node(INFURA_URL)
