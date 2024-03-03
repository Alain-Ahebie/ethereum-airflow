"""
This module contains functions for collecting and processing Ethereum blockchain data.

It includes functionality to connect to an Ethereum node, fetch transactions within a 
specified block range, and save these transactions to a Parquet file. Additionally, 
it provides utilities for uploading the collected data to Google Cloud Storage.
"""
from pathlib import Path
import time
import logging
import datetime
import pandas as pd
from web3 import Web3
from web3.exceptions import Web3Exception
from google.cloud import storage


# Current script path
script_path = Path(__file__).resolve()
# Move up one level up
one_levels_up = script_path.parents[1]
# get the current date
today = datetime.datetime.now().strftime("%Y-%m-%d")
# Include the path and date in the filename
log_filename = f'{one_levels_up}/logs/ethereum_data_collector_{today}.log'


logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_execution_time(func):
    """Decorator to log the execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@log_execution_time
def connect_to_ethereum_node(url):
    """
    Connects to an Ethereum node using the provided URL.

    Parameters:
    - url (str): URL of the Ethereum node, including protocol and port if necessary.

    Returns:
    - Web3 instance connected to the specified Ethereum node. Raises ConnectionError
      on failure.

    Raises:
    - ConnectionError: If connection fails or an error occurs during connection.

    Attempts to establish a connection to an Ethereum node. On success, prints a
    confirmation and returns the Web3 instance. Otherwise, raises ConnectionError with
    details.
    """
    try:
        web3 = Web3(Web3.HTTPProvider(url))
        if not web3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum node")
        else :
            print(f'Connected: {web3.is_connected()}')
            return web3
    except Web3Exception as e:
        raise ConnectionError(f"An error occurred while connecting: {str(e)}")

def fetch_receipt_with_backoff(web3, tx_hash, max_attempts=5):
    """
    Attempts to fetch a transaction receipt with exponential backoff.

    Parameters:
    - web3: The Web3 instance connected to an Ethereum node.
    - tx_hash: The hash of the transaction for which to fetch the receipt.
    - max_attempts: Maximum number of attempts to fetch the receipt.

    Returns:
    - The transaction receipt if successful, None otherwise.
    """
    attempt = 0
    wait_time = 1  # start with 1 second
    while attempt < max_attempts:
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            return receipt  # success, exit the function with the receipt
        except Exception as e:  # Catching a generic exception for the example; specify as needed
            logging.warning(f"Attempt {attempt + 1} failed for transaction {tx_hash.hex()}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(wait_time)
                wait_time *= 2  # double the wait time for the next attempt
                attempt += 1
            else:
                logging.error(f"""Failed to fetch receipt for {tx_hash.hex()}
                              after {max_attempts} attempts at {datetime.now()}.""")
                return None

@log_execution_time
def get_block_one_hour_ago(web3, latest_block):
    """
    Finds the block number closest to one hour ago from the latest block.

    Parameters:
    - web3: Web3 instance for Ethereum blockchain interaction.
    - latest_block: Number of the most recent block.

    Returns:
    - Block number closest to one hour ago. Returns genesis block (0) if it reaches
      the start without finding such a block.

    Iterates backwards from the latest block, comparing each block's timestamp to
    one hour ago until it finds the closest block.
    """
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

@log_execution_time
def get_transactions(web3, start_block, end_block):
    """
    Retrieves transactions between the specified start and end blocks from the Ethereum blockchain.

    Parameters:
    - web3: An instance of Web3 connected to an Ethereum node.
    - start_block: The starting block number from which to retrieve transactions.
    - end_block: The ending block number until which to retrieve transactions.

    Returns:
    - A list of dictionaries, each representing a transaction within the specified block range. 
      each dictionary contains details of the transaction, such as hash, sender and receiver
      addresses, value transferred,gas price, gas used, and more.

    Note:
    - This function uses an exponential backoff strategy to fetch transaction receipts, improving 
    reliability under rate limit constraints.
    """

    # Initialize an empty list to store transaction details
    transactions = []

    # Iterate over each block in the specified range
    for block_number in range(start_block, end_block + 1):
        try:
            # Fetch the block with full transactions details
            block = web3.eth.get_block(block_number, full_transactions=True)
            # Iterate over each transaction in the block
            for tx in block.transactions:
                # Use a helper function with exponential backoff to fetch the transaction receipt
                receipt = fetch_receipt_with_backoff(web3, tx.hash)
                # If the receipt is None, the maximum retry limit was reached; skip this transaction
                if receipt is None:
                    continue

                # Append a dictionary with transaction details to the transactions list
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

@log_execution_time
def save_to_parquet(data, filename):
    """
    Saves the transaction data to a Parquet file.
    
    Parameters:
    - data: The data to be saved.
    - filename: The path and name of the file where data should be saved. Can be a string or a Path object.
    """
    # Convert filename to a Path object (if it's not already one)
    filename = Path(filename)

    # Ensure the directory exists
    filename.parent.mkdir(parents=True, exist_ok=True)

    # Convert the data to a DataFrame and save it as a Parquet file
    df = pd.DataFrame(data)
    df.to_parquet(filename)

    print(f"Data successfully saved to {filename}")

@log_execution_time
def upload_to_gcs(bucket_name, source_file_path):
    """
    Uploads a file to Google Cloud Storage, organized by year/month/day.

    Parameters:
    - bucket_name (str): The name of the Google Cloud Storage bucket where the file will be uploaded.
    - source_file_path (str or Path): The full path to the file that will be uploaded, 
        This can be a string or a Path object.
    """
    # Convert source_file_path to a Path object to easily extract the filename
    source_file_path = Path(source_file_path)
    source_file_name = source_file_path.name

    # Determine the current date and time for folder organization
    now = datetime.datetime.now()
    destination_blob_name = f"year={now.year}/{now.strftime('%m')}/{now.strftime('%d')}/{source_file_name}"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Use the full path for uploading the file
    blob.upload_from_filename(str(source_file_path))
    print(f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}.")
