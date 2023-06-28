import os
import timeit
from web3 import Web3
from dotenv import load_dotenv

load_dotenv(override=True)

# create a .env file
ALCHEMY_FREE_RPC_URL = os.getenv('ALCHEMY_FREE_RPC_URL')
ALCHEMY_PAID_RPC_URL = os.getenv('ALCHEMY_PAID_RPC_URL')


def benchmark_tx_requests(w3: Web3, block_number: int):
    for i in range(block_number - 100, block_number):
        b = w3.eth.get_block(i)
        # print(f'{i}/{block_number}', b)


def benchmark_contract_call(w3: Web3):
    # USDC/ETH 0.05% pool
    uniswap_v3_pool_address = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'  # checksum address
    uniswap_v3_pool_abi = [
        {
            'inputs': [],
            'name': 'factory',
            'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
            'stateMutability': 'view',
            'type': 'function'
        }
    ]
    pool = w3.eth.contract(address=uniswap_v3_pool_address, abi=uniswap_v3_pool_abi)
    factory_address = pool.functions.factory().call()
    # print(factory_address)


if __name__ == '__main__':
    free_w3 = Web3(Web3.HTTPProvider(ALCHEMY_FREE_RPC_URL))
    paid_w3 = Web3(Web3.HTTPProvider(ALCHEMY_PAID_RPC_URL))
    local_w3 = Web3(Web3.HTTPProvider('http://192.168.200.182:8545'))  # you need a local node for this

    block_number = free_w3.eth.get_block('latest').number

    # TX requests
    t1 = timeit.timeit(lambda: benchmark_tx_requests(free_w3, block_number), number=1)
    print(f'Free tier: {t1} seconds')  # 26.88 seconds

    t2 = timeit.timeit(lambda: benchmark_tx_requests(paid_w3, block_number), number=1)
    print(f'Paid tier: {t2} seconds')  # 28 seconds

    t3 = timeit.timeit(lambda: benchmark_tx_requests(local_w3, block_number), number=1)
    print(f'Local: {t3} seconds')  # 0.54 seconds

    # Contract calls
    t1 = timeit.timeit(lambda: benchmark_contract_call(free_w3), number=10)
    print(f'Free tier: {t1 / 10.0} seconds')

    t2 = timeit.timeit(lambda: benchmark_contract_call(paid_w3), number=10)
    print(f'Paid tier: {t2 / 10.0} seconds')

    t3 = timeit.timeit(lambda: benchmark_contract_call(local_w3), number=10)
    print(f'Local: {t3 / 10.0} seconds')