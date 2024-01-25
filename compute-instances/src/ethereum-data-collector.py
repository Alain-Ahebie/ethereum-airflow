from web3 import Web3
import pandas as pd
import datetime

# Connect to an Ethereum node 
"https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
infura_url = "https://mainnet.infura.io/v3/12765045634040aba2c2ae29a97be8d4"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Function to get transactions from a block
def get_transactions(block_number):
    try:
        block = web3.eth.getBlock(block_number, full_transactions=True)
        return [tx for tx in block.transactions if datetime.datetime.utcfromtimestamp(block.timestamp) >= datetime.datetime.utcnow() - datetime.timedelta(hours=1)]
    except Exception as e:
        print(f"Error fetching transactions for block {block_number}: {e}")
        return []

# Check if connection is successful
if not web3.isConnected():
    print("Failed to connect to Ethereum node.")
    exit()

# Fetch the latest block number
latest_block = web3.eth.block_number

# Initialize a list to store transaction data
transactions_data = []

# Iterate over blocks from the latest to the past until we cover the last hour
for block_number in range(latest_block, 0, -1):
    transactions = get_transactions(block_number)
    if not transactions:
        break  # Break the loop if no transactions in the last hour are found in the block

    for tx in transactions:
        # Extract required fields from each transaction
        tx_data = {
            "hash": tx.hash.hex(),
            "nonce": tx.nonce,
            "block_hash": tx.blockHash.hex(),
            "block_number": tx.blockNumber,
            "transaction_index": tx.transactionIndex,
            "from_address": tx['from'],
            "to_address": tx.to,
            "value": web3.fromWei(tx.value, 'ether'),  # Convert value from Wei to Ether
            "gas": tx.gas,
            "gas_price": web3.fromWei(tx.gasPrice, 'gwei'),  # Convert gas price to Gwei
            "input": tx.input,
            "block_timestamp": datetime.datetime.utcfromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "max_fee_per_gas": web3.fromWei(tx.get('maxFeePerGas'), 'gwei') if tx.get('maxFeePerGas') else None,
            "max_priority_fee_per_gas": web3.fromWei(tx.get('maxPriorityFeePerGas'), 'gwei') if tx.get('maxPriorityFeePerGas') else None,
            "transaction_type": tx.type
        }
        transactions_data.append(tx_data)

# Convert to DataFrame
df = pd.DataFrame(transactions_data)

# Print or save DataFrame
print(df)
# df.to_csv('ethereum_transactions_last_hour.csv')
