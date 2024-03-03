"""
This module contains the main entry point for the application.

It demonstrates how to interact with the Ethereum blockchain,
fetch transactions between specified blocks, and process them
for further analysis or storage.
"""
from pathlib import Path
import logging
import datetime
from src import ethereum_data_collector as edc

# Current script path
script_path = Path(__file__).resolve()
#select current directory
current_dir = script_path.parents[0]
# get the current date
today = datetime.datetime.now().strftime("%Y-%m-%d")
# Include the path and date in the filename
log_filename = f'{current_dir}/logs/ethereum_data_collector_{today}.log'
# Set your Ethereum node URL
INFURA_URL = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"

def main():
    """
    Main function to orchestrate the process flow.

    This function performs the following steps:
    1. Connects to an Ethereum node.
    2. Fetches the latest block number.
    3. Determines the start block based on a time offset.
    4. Fetches transactions between the start block and the latest block.
    5. Saves the transactions to a Parquet file.
    6. Uploads the Parquet file to Google Cloud Storage.
    """
    logging.info("START --------------------------------------------------------")
    try:
        # Connect to Ethereum node
        web3 = edc.connect_to_ethereum_node(INFURA_URL)
        logging.info("Connected to Ethereum node.")

        # Get the latest block number
        latest_block = web3.eth.get_block('latest').number
        logging.info("Latest block number: %s", latest_block)

        # Find the start block (one hour ago or one minute ago)
        start_block = edc.get_block_one_hour_ago(web3, latest_block)
        logging.info("Start block (one hour ago): %s", start_block)

        # Fetch transactions between start block and latest block
        transactions = edc.get_transactions(web3, start_block, latest_block)
        logging.info("Transactions fetched successfully.")

        # Generate filename with current timestamp for the Parquet file
        current_time_str = edc.datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        parquet_filename = f'ethereum_transactions_{current_time_str}.parquet'
        files_folder =  f'{current_dir}/files/{parquet_filename}'

        # Save transactions to a Parquet file
        edc.save_to_parquet(transactions, files_folder)
        logging.info("Transactions saved to %s .",parquet_filename)

        # Upload the Parquet file to Google Cloud Storage
        edc.upload_to_gcs('evm_data', files_folder)
        logging.info("File uploaded to Google Cloud Storage: %s .",parquet_filename)
        logging.info("END --------------------------------------------------------")
    except Exception as e:
        logging.error("Error in main execution: %s", e)
        raise

if __name__ == "__main__":
    main()
