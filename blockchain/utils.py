import os
import json
from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import ExtraDataToPOAMiddleware

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = "./blockchain/.env"
load_dotenv(env_path)

# Загрузка окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Инициализация подключения
w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_NODE_URL")))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Загрузка ABI
with open(os.path.join(os.path.dirname(__file__), 'abi.json')) as f:
    abi = json.load(f)

# Создание объекта контракта
contract = w3.eth.contract(
    address=os.getenv("CONTRACT_ADDRESS"),
    abi=abi
)

def record_vote(vote_id: str, result_hash: str) -> str:
    """Записывает результаты голосования в блокчейн"""
    account = w3.eth.account.from_key(os.getenv("OWNER_PRIVATE_KEY"))
    
    tx = contract.functions.recordVote(vote_id, result_hash).build_transaction({
        'chainId': 1337,
        'gas': 200000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })
    
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return tx_hash.hex()

def get_vote_record(vote_id: str) -> str:
    """Читает результаты голосования из блокчейна"""
    return contract.functions.getRecord(vote_id).call()