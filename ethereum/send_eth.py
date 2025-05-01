from web3 import Web3, HTTPProvider, Account
from web3.exceptions import TransactionNotFound, BadFunctionCallOutput
from otp.send_email import send_email
import os, dotenv


dotenv.load_dotenv()
private_key = os.environ.get('faucet_key') # pk on sepolia and testnet should be the same. therefore cant use the default keys.
faucet_account = Account.from_key(private_key)
eth_distribution_amount = int(0.452*10**18)

def get_bumped_gas_price(web3_instance, address, nonce):
    try:
        # Look for a pending transaction with the same nonce
        txpool_content = web3_instance.geth.txpool.content()
        pending_txs = txpool_content['pending'].get(address.lower(), {})
        if str(nonce) in pending_txs:
            current_price = int(pending_txs[str(nonce)]['gasPrice'], 16)
            bumped_price = int(current_price * 1.2)  # 20% bump
            return bumped_price
    except Exception as e:
        print("Couldn't fetch txpool content:", e)

    # Fallback to a default if no tx found
    return web3_instance.to_wei(60, 'gwei')


async def send_eth(address, rpc):
    print(rpc)
    web3_instance = Web3(HTTPProvider(rpc)) # either sepolia or qut testnet
    # check there is enough to send before attempting, if not, return an error message
        
    try:
        nonce = web3_instance.eth.get_transaction_count(faucet_account.address, "pending")
        gas_price = get_bumped_gas_price(web3_instance, faucet_account.address, nonce)

        tx = {
            'nonce': nonce,
            'to': address,
            'value': eth_distribution_amount,
            'gas': 200000,
            'gasPrice': gas_price

        }
        signed_tx = web3_instance.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)
        status = 'success'
        return status, tx_hash.hex()
    except (TransactionNotFound, BadFunctionCallOutput) as e:
        print(f'Transaction error: {e}')
        status = 'error'
        return status, None
    except Exception as e:
        print(f'Unexpected error: {e}')
        status = 'error'
        return status, None

