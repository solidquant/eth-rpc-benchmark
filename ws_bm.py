import os
import csv
import json
import asyncio
import datetime
import pandas as pd
from web3 import Web3
from pathlib import Path
from websockets import connect
from dotenv import load_dotenv
from multiprocessing import Process

load_dotenv(override=True)

LOG_DIR = Path('./logs')
os.makedirs(LOG_DIR, exist_ok=True)

ALCHEMY_API_KEY = os.getenv('ALCHEMY_PAID_RPC_URL').split('/')[-1]

PAID_URL = f'wss://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}'
LOCAL_URL = 'ws://192.168.200.182:8546'

web3 = Web3(Web3.WebsocketProvider(PAID_URL))


async def stream_events(url: str, log_filename: str):
    async with connect(url) as ws:
        usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
        transfer_event = web3.keccak(text='Transfer(address,address,uint256)')
        subscription = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_subscribe',
            'params': [
                'logs',
                {'address': usdt_address, 'topics': [transfer_event.hex()]}
            ]
        }
        await ws.send(json.dumps(subscription))
        subscription_response = await ws.recv()
        print(subscription_response)

        f = open(LOG_DIR / log_filename, 'w', newline='')
        log = csv.writer(f)

        last_updated = datetime.datetime.now()

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                response = json.loads(message)
                params = response['params']['result']

                log.writerow([
                    params['blockNumber'],
                    params['transactionIndex'],
                    params['logIndex'],
                    datetime.datetime.now().timestamp()
                ])

                # run stream for 60 * 60 seconds (1 hour)
                now = datetime.datetime.now()
                if (now - last_updated).total_seconds() >= 60 * 60:
                    f.close()
                    print(f'{log_filename} complete')
                    break

            except Exception as e:
                # error handling here
                raise e


def stream(url: str, log_filename: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream_events(url, log_filename))


if __name__ == '__main__':
    p1 = Process(target=stream, args=(PAID_URL, 'paid.csv'))
    p2 = Process(target=stream, args=(LOCAL_URL, 'local.csv'))

    _ = [p.start() for p in [p1, p2]]
    __ = [p.join() for p in [p1, p2]]

    paid_log_df = pd.read_csv(LOG_DIR / 'paid.csv', header=None)
    local_log_df = pd.read_csv(LOG_DIR / 'local.csv', header=None)

    log = pd.merge(paid_log_df, local_log_df, on=[0, 1, 2])
    log.columns = ['block', 'tx', 'log', 'paid', 'local']
    log['latency'] = log['paid'] - log['local']

    print(f'Average latency in seconds: {log["latency"].mean()}')

    print(log['latency'])
