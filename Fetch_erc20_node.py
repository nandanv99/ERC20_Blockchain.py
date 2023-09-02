from web3 import Web3
from datetime import datetime as dt
import datetime
import json
import pandas as pd
import requests
import multiprocessing
import asyncio
from pprint import pprint
import time 
from io import StringIO


node_url = "< Erigon node URL >" 
API_KEY = '< Etherscan API key >' 
erc_20_contract = "< erc 20 contract from ETH ex: 0xCb288b6d30738db7E3998159d192615769794B5b >" 


result = []
result_json={
    "result":[]
}


# Create the node connection
web3 = Web3(Web3.HTTPProvider(node_url))

# Verify if the connection is successful
if web3.isConnected():
    print("-" * 50)
    print("Connection Successful")
    print("-" * 50)
else:
    print("Connection Failed")

def get_unix_timestamp(date_string):
    # Convert date string to datetime object
    date_obj = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    # Convert datetime object to Unix timestamp
    unix_timestamp = int(date_obj.timestamp())

    # Return Unix timestamp
    return unix_timestamp


def get_block_number(timestamp, api_key):
    url = 'https://api.etherscan.io/api'
    payload = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': timestamp,
        'closest': 'before',
        'apikey': api_key
    }

    response = requests.get(url, params=payload)
    content = response.content

    response_dict = json.loads(content)
    block_number = response_dict['result']

    return block_number

def get_decimal(api_key,contract_add):
    normal_list="https://api.etherscan.io/api?module=account&action=tokentx&address="+contract_add+"&startblock=StartBlockNumber&endblock=EndBlockNumber&offset=100&sort=asc&apikey="+api_key
    y = requests.get(normal_list)
    df=pd.read_json(StringIO(y.text))
    dec=len("0"*int(df.result.iloc[1]['tokenDecimal']))
    return dec

decimal=get_decimal(API_KEY,erc_20_contract)

# Function to encode a hex string as an Ethereum event topic
def encode_topic(value):
    add_padding = value[2:].zfill(64) 
    encoded_topic = '0x' + add_padding
    return encoded_topic

# Function to decode an encoded Ethereum event topic back into its original hex string
def decode_topic(encoded_value):
    decoded_value = '0x' + encoded_value[2:].lstrip('0')
    return decoded_value

# Function to convert a hex string to a decimal integer
def to_decimal(hex_string):
    bytes_value = Web3.toBytes(hexstr=hex_string)
    decimal_value = int.from_bytes(bytes_value, byteorder='big')
    return decimal_value 

# Function to convert a number with decimals to an integer value
# Note: this function is specifically for the USDT token, which has 6 decimal places
def convert_to_usdt(number_with_decimals,length):
    number_without_decimals = number_with_decimals // (10**length)
    return number_without_decimals

# Convert Wei to Ether
def wei_to_eth(wei):
    eth_value = Web3.fromWei(wei, 'ether')
    return eth_value

def find_trnas(txhash,address):
    alltx=[]
    tx_receipt = web3.eth.get_transaction_receipt(txhash)
    for log in tx_receipt["logs"]:
        if len(log["topics"]) == 3:
            topic1_decoded = decode_topic(log["topics"][1].hex())
            topic2_decoded = decode_topic(log["topics"][2].hex())
            if topic1_decoded==address.lower() or topic2_decoded==address.lower():
                log_entry = {
                    'from': topic1_decoded,
                    'to': topic2_decoded,
                    'value': convert_to_usdt(to_decimal(decode_topic(log['data'])),decimal),
                    'hash': txhash
                }
                alltx.append(log_entry)
    return alltx



def main():
    
    unique_add=[]
    checksum_address = web3.toChecksumAddress(erc_20_contract)

    # Encode a wallet address. This in case you want to track the transfers only from this address.
    address_to_track = '0x95b564f3b3bae3f206aa418667ba000afafacc8a'
    encoded_address = encode_topic(address_to_track)

    # The topics define which event to track; the ERC-20 transfer in this case
    logs_topics = [
        '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
        # '0x9344f1a0460e7d82a14a16b325b7b5f30a0e9aec0f2de30b9ca95066bdc0c27e'
    ]

    transfer_topic = web3.keccak(text='Transfer(address,address,uint256)').hex()
    
    # result.append('from_address','to_address','value_converted','transaction_hash')

    days = 3   # How many days in the past to get
    end_day = 22 # The limit of the search. In this case today

    # start_date_new = datetime.date(2020, 3, 1)
    start_date_new = datetime.date(2021, 3, 1)
    end_date_new = datetime.date(2023, 3, 31)
    delta = datetime.timedelta(days=30)

    while start_date_new < end_date_new:
        try:
            print('Getting logs...')
            end_of_range = start_date_new + delta
            start_date = start_date_new.strftime("%Y-%m-%d 00:00:00")
            timestamp = get_unix_timestamp(start_date)
            start_block = get_block_number(timestamp, API_KEY)


            end_date = end_of_range.strftime("%Y-%m-%d 00:00:00")
            end_timestamp = get_unix_timestamp(end_date)
            end_block = get_block_number(end_timestamp, API_KEY)
            start_date_new += delta



            filter = {
                'fromBlock': int(start_block),
                'toBlock': int(end_block),
                'address': checksum_address,
                'topics': logs_topics
            }

            raw_logs = web3.eth.get_logs(filter)
            # raw_logs = web3.eth.getLogs(filter)


            for log in raw_logs:
                extracted_data = {key: log[key] for key in ['address', 'topics', 'data', 'transactionHash'] if key in log}
                # print(extracted_data)

                # address = extracted_data.get('address')
                # topics = extracted_data.get('topics')
                # data = extracted_data.get('data')
                transaction_hash = str(extracted_data.get('transactionHash').hex()).lower()

                # if topics:
                #     topics_str = [topic.hex() for topic in topics]

                # from_address = decode_topic(topics_str[1])
                # to_address = decode_topic(topics_str[2])
                # value_transferred = decode_topic(data)
                # value_hex = convert_to_usdt(to_decimal(value_transferred),decimal)
                # value_converted = wei_to_eth(to_decimal(value_transferred))

                # data=find_trnas(transaction_hash,erc_20_contract)
                unique_add.append(transaction_hash)

                # print("txs : ",transaction_hash,"\nvalue transafered ",value_transferred,"\nvalue hex : ",value_hex)

                # log_entry = {
                #     'from': from_address,
                #     'to': to_address,
                #     'value': float(value_hex),
                #     'hash': transaction_hash
                # }

                # -----------------------------------------
                # result.extend(data)
                # result_json["result"].extend(data)

                

            end_day -= 1
            days -= 1
            print(f'Retrieved logs between block {start_block} and block {end_block}')
        except Exception as er:
            print("error!!")
            print(er)
            pass
        
    unique_add=set(unique_add)
    start=time.time()
    for i,k in zip(unique_add,range(len(unique_add))):
        print(k)
        data=find_trnas(i,erc_20_contract)
        result.extend(data)
        result_json["result"].extend(data)

    print("set : ",len(unique_add))
    df = pd.DataFrame.from_dict(result_json["result"])
    df.to_json("whole_data.json",indent=2,orient='records')
    end=time.time()
    print(end-start)
    
    return unique_add

if __name__ == "__main__":
    main()
    # unique_add=main()
    # pool=multiprocessing.Pool()
    # def process_txhash(txhash):
    #     return find_trnas(txhash, "abc")

    # with pool as pools:
    #     for data in pools.map(process_txhash, unique_add):
    #         result.extend(data)
    #         result_json["result"].extend(data)

    # print("set : ",len(unique_add))
    # df = pd.DataFrame.from_dict(result_json["result"])
    # df.to_json("whole_data.json",indent=2,orient='records')



    