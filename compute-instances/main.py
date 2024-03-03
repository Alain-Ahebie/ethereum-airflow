from src import ethereum_data_collector as edc
from pathlib import Path
import logging
import datetime
import os

"""Implementing Exponential Backoff to avoid rate limit !!"""

# Current script path
script_path = Path(__file__).resolve()
#select current directory
current_dir = script_path.parents[0]
# get the current date
today = datetime.datetime.now().strftime("%Y-%m-%d")
# Include the path and date in the filename
log_filename = f'{current_dir}/logs/ethereum_data_collector_{today}.log'

def main():
    logging.info("START --------------------------------------------------------")
    try:
        # Set your Ethereum node URL
        INFURA_URL = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"

        # Connect to Ethereum node
        web3 = edc.connect_to_ethereum_node(INFURA_URL)
        logging.info("Connected to Ethereum node.")

        # Get the latest block number
        latest_block = web3.eth.get_block('latest').number
        logging.info(f"Latest block number: {latest_block}")

        # Find the start block (one hour ago or one minute ago)
        start_block = edc.get_block_one_hour_ago(web3, latest_block)
        logging.info(f"Start block (one hour ago): {start_block}")

        # Fetch transactions between start block and latest block
        transactions = edc.get_transactions(web3, start_block, latest_block)
        logging.info("Transactions fetched successfully.")

        # Generate filename with current timestamp for the Parquet file
        current_time_str = edc.datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        parquet_filename = f'ethereum_transactions_{current_time_str}.parquet'
        files_folder =  f'{current_dir}/files/{parquet_filename}'

        # Save transactions to a Parquet file
        edc.save_to_parquet(transactions, files_folder)
        logging.info(f"Transactions saved to {parquet_filename}.")

        # Upload the Parquet file to Google Cloud Storage
        # print(f"Attempting to upload file at path: {files_folder}/ethereum_transactions_20240302235715.parquet")
        edc.upload_to_gcs('evm_data', files_folder)
        logging.info(f"File uploaded to Google Cloud Storage: {parquet_filename}.")
        logging.info("END --------------------------------------------------------")
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
