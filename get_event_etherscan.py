import asyncio
import json
import websockets
from web3 import Web3
import requests

# Replace with your own Ethereum node WebSocket URL
eth_node_ws_url = ''

# Contract Address on Ethereum Mainnet
CONTRACT_ADDRESS = ""

# Transfer Event Signature
EVENT_SIGNATURE = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# Etherscan API key
ETHERSCAN_API_KEY = ""

def block_number_to_hex(block_number):
    # Convert block number to hexadecimal
    hex_block_number = "0x" + hex(block_number)[2:]
    return hex_block_number

def wei_to_usd(wei_amount):
    # Get the current USD price of Ether from Etherscan API
    url = f"<https://api.etherscan.io/api?module=stats&action=tokeninfo&contractaddress={CONTRACT_ADDRESS}&apikey={ETHERSCAN_API_KEY}>"
    response = requests.get(url).json()

    # Get Ether/USD exchange rate
    eth_price_usd = float(response['result']['ethusd'])

    # Convert Wei to Ether
    ether_amount = Web3.from_wei(wei_amount, "ether")

    # Convert Ether to USD
    usd_amount = float(ether_amount) * eth_price_usd

    return usd_amount

async def subscribe_to__logs(ws_url):
    # Continuously try to connect and subscribe
    while True:
        try:
            # Establish a WebSocket connection to the Ethereum node
            async with websockets.connect(ws_url) as websocket:
                # Send a subscription request for the Transfer event logs
                await websocket.send(json.dumps({
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        "logs",
                        {
                            "address": CONTRACT_ADDRESS,
                            "fromBlock": FROM_BLOCK,
                            "topics": [EVENT_SIGNATURE]
                        }
                    ],
                    "jsonrpc": "2.0"
                }))

                # Wait for the subscription response and print it
                subscription_response = await websocket.recv()
                print(f'Subscription response: {subscription_response}')

                # Continuously process incoming logs
                while True:
                    # Receive a log entry and parse it as JSON
                    log = await websocket.recv()
                    log_data = json.loads(log)

                    # Decode the log data
                    #Print log data
                    print(f'Log Data : {log_data}')

                    # Convert the transfer amount to USD and print it
                    transfer_amount = int(log_data["params"]["result"]["data"], 16)
                    usd_amount = wei_to_usd(transfer_amount)
                    print(f'Transfer Amount (USD): {usd_amount}')

                    # Print separator
                    print("#" * 10)

        # If there's an exception (e.g., connection error), attempt to reconnect
        except Exception as e:
            print(f'Error: {e}')
            print('Reconnecting...')
            await asyncio.sleep(5)

# From and To block parameters (use 'latest' for the most recent block)
FROM_BLOCK = block_number_to_hex(15940222)



# Execute the subscription function
asyncio.run(subscribe_to__logs(eth_node_ws_url))
