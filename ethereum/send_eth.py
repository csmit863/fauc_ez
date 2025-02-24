from web3 import Web3, HTTPProvider, Account
from web3.exceptions import TransactionNotFound, BadFunctionCallOutput
from otp.send_email import send_email
import os, dotenv


dotenv.load_dotenv()
web3_instance = Web3(HTTPProvider(os.environ.get('web3_provider')))
private_key = os.environ.get('faucet_key')
faucet_account = Account.from_key(private_key)
eth_distribution_amount = int(0.452*10**18)


async def send_eth(address):
    # check there is enough to send before attempting, if not, return an error message
    nonce = web3_instance.eth.get_transaction_count(faucet_account.address)    
    try:
        tx = {
            'nonce': nonce,
            'to': address,
            'value': eth_distribution_amount,
            'gas': 200000,
            'gasPrice': web3_instance.to_wei(50, 'gwei')
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

