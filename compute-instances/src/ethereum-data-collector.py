import datetime
import pandas as pd
from web3 import Web3
from web3.exceptions import Web3Exception
from google.cloud import storage

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
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
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

def get_transactions(web3, start_block, end_block):
    # Retrieves transactions between the specified start and end blocks
    transactions = []
    for block_number in range(start_block, end_block + 1):
        try:
            block = web3.eth.get_block(block_number, full_transactions=True)
            for tx in block.transactions:
                receipt = web3.eth.get_transaction_receipt(tx.hash)
                transactions.append({
                    "Hash": tx.hash.hex(),  # Unique identifier of the transaction
                    "From": tx['from'],  # Sender's Ethereum address
                    "To": tx.to,  # Recipient's Ethereum address (None for contract creations)
                    "Value": web3.from_wei(tx.value, 'ether'),  # Amount of Ether transferred
                    "GasPrice": web3.from_wei(tx.gasPrice, 'gwei'),  # Gas price per unit in Gwei
                    "GasLimit": tx.gas,  # Maximum gas provided by the sender
                    "GasUsed": receipt.gasUsed,  # Total gas used in the transaction
                    "TransactionFee": web3.from_wei(receipt.gasUsed * tx.gasPrice, 'ether'),  # Total transaction fee
                    "Nonce": tx.nonce,  # Sequence number issued by the sender
                    "BlockNumber": tx.blockNumber,  # Block number containing the transaction
                    "BlockHash": tx.blockHash.hex(),  # Hash of the block containing the transaction
                    "BlockTimestamp": datetime.datetime.fromtimestamp(block.timestamp),  # Time when the block was mined
                    "TransactionIndex": tx.transactionIndex,  # Transaction's index position in the block
                    "CumulativeGasUsed": receipt.cumulativeGasUsed,  # Cumulative gas used in the block up to this transaction
                    # "Logs": [dict(log) for log in receipt.logs]  ,  # Event logs emitted by this transaction
                    # "LogsBloom": receipt.logsBloom.hex(),  # Bloom filter for light clients
                    "Status": receipt.status,  # Status of the transaction (1 = success, 0 = failure)
                    "ContractAddress": receipt.contractAddress if receipt.contractAddress else None,  # Contract address created, if any
                    "Root": receipt.root if 'root' in receipt else None,  # State root after the transaction (pre-Byzantium forks)
                    "IsError": 0 if receipt.status == 1 else 1  # Flag indicating if the transaction was erroneous
                })
        except Web3Exception as e:
            print(f"An error occurred while processing block {block_number}: {str(e)}")
            pass  # Continue with the next iteration even if an error occurs
    return transactions

def save_to_parquet(data, filename):
    # Saves the transaction data to a Parquet file
    df = pd.DataFrame(data)
    df.to_parquet(filename)
    
    
def upload_to_gcs(bucket_name, source_file_name):
    """Uploads a file to Google Cloud Storage, organized by year/month/day."""
    # Determine the current date and time for folder organization
    now = datetime.datetime.now()
    destination_blob_name = f"year={now.year}/{now.strftime('%m')}/{now.strftime('%d')}/{source_file_name}"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}.")    
    
# INFURA_URL = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"   
# web3 = connect_to_ethereum_node(INFURA_URL)
# latest_block = web3.eth.get_block('latest').number
# start_block = get_block_one_hour_ago(web3, latest_block)    
# transactions = get_transactions(web3, start_block, latest_block)
# save_to_parquet(transactions, 'ethereum_transactions_last_min.parquet')


upload_to_gcs('evm_bucket', "ethereum_transactions_last_min.parquet")

