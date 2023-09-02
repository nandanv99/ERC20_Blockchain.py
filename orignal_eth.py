import datetime
import pandas as pd
from io import StringIO
import requests
from datetime import datetime as dt
import json
import time

# Replace this with your Etherscan API key
API_KEY = ""

def get_unix_timestamp(date_string):
    date_obj = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    unix_timestamp = int(date_obj.timestamp())
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


def process_date_range(args):
    start_date_new, delta, API_KEY, contract = args
    end_of_range = start_date_new + delta
    start_date = start_date_new.strftime("%Y-%m-%d 00:00:00")
    timestamp = get_unix_timestamp(start_date)
    start_block = get_block_number(timestamp, API_KEY)

    end_date = end_of_range.strftime("%Y-%m-%d 00:00:00")
    end_timestamp = get_unix_timestamp(end_date)
    end_block = get_block_number(end_timestamp, API_KEY)

    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={contract}&page=1&offset=9999&startblock={start_block}&endblock={end_block}&sort=asc&apikey={API_KEY}"
    response = requests.get(url)
    content = response.text
    df = pd.read_json(StringIO(content))
    return df

def main(contract):
    df=pd.DataFrame()
    dfs = []
    days = 3   # How many days in the past to get
    end_day = 22 # The limit of the search. In this case today
    start_date_new = datetime.date(2022, 3, 1)
    end_date_new = datetime.date(2023, 3, 31)
    delta = datetime.timedelta(days=30)

    

    while start_date_new < end_date_new:

        print('Getting logs...')
        end_of_range = start_date_new + delta
        start_date = start_date_new.strftime("%Y-%m-%d 00:00:00")
        timestamp = get_unix_timestamp(start_date)
        start_block = get_block_number(timestamp, API_KEY)


        end_date = end_of_range.strftime("%Y-%m-%d 00:00:00")
        end_timestamp = get_unix_timestamp(end_date)
        end_block = get_block_number(end_timestamp, API_KEY)
        start_date_new += delta
        url=f"https://api.etherscan.io/api?module=account&action=tokentx&address={contract}&page=1&offset=9999&startblock={start_block}&endblock={end_block}&sort=asc&apikey={API_KEY}"
        y=requests.get(url)

        data = y.json()
        result = data["result"]
        df = pd.DataFrame(result)
        dfs.append(df)


        # x=pd.read_json(StringIO(y.text))
        # df=df.append(x)
        print(df.shape)
        print( start_date," -- ", end_date)
        end_day -= 1
        days -= 1

    # df = df['result']
    # df = df.drop_duplicates()
    # df = df.reset_index(drop=True)

    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates().reset_index(drop=True)
    

    print(df.shape)
    print(df.head)
    df.to_csv("data_loop.csv")
    return df

if __name__ == "__main__":
    start = time.time()
    main("0x87986Ae1e99f99Da1f955D16930DC8914fFBED56")
    end = time.time()

    print(end - start)