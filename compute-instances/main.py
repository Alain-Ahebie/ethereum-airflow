from src import ethereum_data_collector as edc


# def main():
#     # Set your Ethereum node URL
#     INFURA_URL = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"

#     # Connect to Ethereum node
#     web3 = edc.connect_to_ethereum_node(INFURA_URL)

#     # Get the latest block number
#     latest_block = web3.eth.get_block('latest').number

#     # Find the start block (one hour ago or one minute ago)
#     start_block = edc.get_block_one_hour_ago(web3, latest_block) 

#     # Fetch transactions between start block and latest block
#     transactions = edc.get_transactions(web3, start_block, latest_block)

#     # Generate filename with current timestamp for the Parquet file
#     current_time_str = edc.datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#     parquet_filename = f'ethereum_transactions_{current_time_str}.parquet'

#     # Save transactions to a Parquet file
#     edc.save_to_parquet(transactions, parquet_filename)

#     # Upload the Parquet file to Google Cloud Storage
#     edc.upload_to_gcs('evm_bucket', parquet_filename)

# if __name__ == "__main__":
#     main()
