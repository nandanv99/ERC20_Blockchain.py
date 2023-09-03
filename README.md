# Fetch ERC20 transactions from any blockchain explorer using this script. It supports a wide range of explorers, including:

- Ethereum (ETH)
- Binance Smart Chain (BSC)
- Polygon (formerly Matic)
- Avalanche (AVAX) via Snowtrace
- Arbitrum
- Optimism

👉🏻 You can use both node connections and API keys from these explorers to retrieve the data.



## ERC20 Token Transaction Data Retrieval for file [orignal.py](https://github.com/nandanv99/ERC20_Blockchain.py/blob/main/orignal_eth.py):
This Python script allows you to fetch ERC20 token transaction data within a specified date range from the Ethereum blockchain using the Etherscan API. It splits the data into multiple CSV files based on a specified time interval.
### Prerequisites:
Before running the script, you need to have the following:
- Python 3 installed on your machine.
- Necessary Python libraries (Pandas) installed.
### Usage:
- Replace API_KEY with your Etherscan API key in the script.

- Specify the ERC20 token contract address you want to retrieve data for in the main function.

- Set the desired date range in the main function:

```
start_date_new: The start date of the date range.
end_date_new: The end date of the date range.
delta: The time interval for each data retrieval (e.g., 30 days).
```
Run the script:
```
python orignal.py
```


## Notes
- You can adjust the days and end_day variables to control the number of data retrieval iterations and the endpoint of your search.
- The script retrieves data in batches to handle large date ranges efficiently.

🧠❤️ Feel free to customize this README to include any additional information or instructions that you think would be helpful.

