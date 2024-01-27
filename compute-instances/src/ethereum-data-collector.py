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
        else :
            print(f'Connected: {web3.is_connected()}')
            return web3
    except Web3Exception as e:
        raise ConnectionError(f"An error occurred while connecting: {str(e)}")
    
def get_block_one_hour_ago(web3, latest_block):
    # Finds the block number that was closest to one hour ago
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    block_number = latest_block
    while True:
        try:
            block = web3.eth.get_block(block_number)
            if block.timestamp <= one_hour_ago.timestamp():
                break
            block_number -= 1
            if block_number == 0:
                break
        except Web3Exception as e:
            print(f"An error occurred while fetching block: {str(e)}")
            break
    print("block_number", block_number)    
    return block_number

INFURA_URL = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"   
web3 = connect_to_ethereum_node(INFURA_URL)
latest_block = web3.eth.get_block('latest').number
get_block_one_hour_ago(web3, latest_block)


