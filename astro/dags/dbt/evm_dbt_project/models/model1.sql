CREATE TABLE IF NOT EXISTS `starclay-medley.eth_data.transactions` (
  `Hash` STRING,  -- Unique identifier of the transaction
  `From` STRING,  -- Sender's Ethereum address
  `To` STRING,    -- Recipient's Ethereum address (None for contract creations)
  `Value` FLOAT64, -- Amount of Ether transferred
  `GasPrice` FLOAT64, -- Gas price per unit in Gwei
  `GasLimit` INT64,  -- Maximum gas provided by the sender
  `GasUsed` INT64,   -- Total gas used in the transaction
  `TransactionFee` FLOAT64, -- Total transaction fee
  `Nonce` INT64,    -- Sequence number issued by the sender
  `BlockNumber` INT64,  -- Block number containing the transaction
  `BlockHash` STRING,  -- Hash of the block containing the transaction
  `BlockTimestamp` TIMESTAMP,  -- Time when the block was mined
  `TransactionIndex` INT64,    -- Transaction's index position in the block
  `CumulativeGasUsed` INT64,  -- Cumulative gas used in the block up to this transaction
  -- "Logs" and "LogsBloom" are omitted as they require more complex schema definition
  `Status` INT64,   -- Status of the transaction (1 = success, 0 = failure)
  `ContractAddress` STRING, -- Contract address created, if any
  `Root` STRING,    -- State root after the transaction (pre-Byzantium forks)
  `IsError` INT64   -- Flag indicating if the transaction was erroneous
)
