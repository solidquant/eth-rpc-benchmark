import os
import json
import asyncio
from web3 import Web3
from websockets import connect
from dotenv import load_dotenv

load_dotenv(override=True)

ALCHEMY_API_KEY = os.getenv('ALCHEMY_PAID_RPC_URL').split('/')[-1]

url = f'wss://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}'
# url = 'ws:''localhost:8546'

web3 = Web3(Web3.WebsocketProvider(url))


async def get_event():
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

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                response = json.loads(message)
                print(response)
                pass
            except Exception as e:
                print(e)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(get_event())
