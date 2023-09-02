import json
import requests
from web3 import Web3
import hashlib


# Replace this with the contract address
contract_address = ""

# Replace this with the event name you want to generate the signature for
event_name = "Transfer"
event_name1 = "Swap"

# Replace these with your Ethereum node's address and API key
eth_node_address = ""

# Replace this with your Etherscan API key
etherscan_api_key = ""


# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider(eth_node_address))

def fetch_contract_abi(contract_address):
 
    # Fetch the contract ABI using Etherscan API
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
    response = requests.get(url)
    abi = json.loads(response.content)['result']
    print(json.loads(abi))

    return json.loads(abi)

def generate_event_signature(abi, event_name):
    # Find the event in the ABI
    event = next(filter(lambda x: x['type'] == 'event' and x['name'] == event_name, abi), None)

    print(event)

    if not event:
        raise Exception(f"Event '{event_name}' not found in the ABI.")

    # Generate the event signature
    inputs = ','.join([f"{arg['type']}" for arg in event['inputs']])
    event_signature = f"{event_name}({inputs})"
    event_signature_hash = w3.keccak(text=event_signature).hex()

    return event_signature_hash



# Fetch the contract ABI
abi = fetch_contract_abi(contract_address)

# Generate the event signature
event_signature_hash = generate_event_signature(abi, event_name)
print(f"Event signature hash for '{event_name}': {event_signature_hash}")
