from web3 import Web3, HTTPProvider, Account
from web3.exceptions import TransactionNotFound, BadFunctionCallOutput
import os
import dotenv
import json

dotenv.load_dotenv()

# Load environment variables
web3_provider = os.environ.get('web3_provider')
web3_instance = Web3(HTTPProvider(web3_provider))
private_key = os.environ.get('faucet_key')
faucet_account = Account.from_key(private_key)

# Load contract ABI and address
contract_address = Web3.to_checksum_address(os.environ.get('contract_address'))

current_dir = os.path.dirname(os.path.abspath(__file__))
abi_path = os.path.join(current_dir, "abi.json")

with open(abi_path, "r") as abi_file:
    contract_abi = json.load(abi_file)

# Initialize contract
contract = web3_instance.eth.contract(address=contract_address, abi=contract_abi)

async def send_create_membership_tx(wallet_address: str, student_number: str):
    
    """
    Interacts with the smart contract's mintMembership function to mint an NFT for the given student number.
    """
    try:
        # Ensure wallet_address is valid
        if not Web3.is_address(wallet_address):
            return "error: invalid wallet address", None

        # Build the transaction
        nonce = web3_instance.eth.get_transaction_count(faucet_account.address)
        transaction = contract.functions.mintMembership(
            Web3.to_checksum_address(wallet_address),
            int(student_number)
        ).build_transaction({
            'chainId': web3_instance.eth.chain_id,
            'gas': 200000,  # Estimate appropriate gas limit
            'gasPrice': web3_instance.to_wei(50, 'gwei'),
            'nonce': nonce
        })
        # Sign and send the transaction
        signed_tx = web3_instance.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Return success with transaction hash
        return "success", tx_hash.hex()

    except (TransactionNotFound, BadFunctionCallOutput) as e:
        print(f'Transaction error: {e}')
        return "error", None

    except Exception as e:
        print(f'Unexpected error: {e}')
        return "error", None

