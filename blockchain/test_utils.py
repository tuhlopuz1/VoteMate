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

def create_vote_topic(title: str, options: list) -> int:
    """Создаёт новый топик голосования и возвращает его ID"""

    account = w3.eth.account.from_key(os.getenv("OWNER_PRIVATE_KEY"))
    
    tx = contract.functions.createTopic(title, options).build_transaction({
        'chainId': 1337,
        'gas': 300000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Транзакция отправлена: {tx_hash.hex()}")

    # Ждём подтверждения
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Парсим событие TopicCreated
    events = contract.events.TopicCreated().process_receipt(receipt)

    if len(events) == 0:
        raise Exception("Событие TopicCreated не найдено в транзакции")

    topic_id = events[0]['args']['topicId']
    print(f"Создан новый топик с ID: {topic_id}")

    return topic_id

def get_topic_details(topic_id: str) -> dict:
    """Получает детали топика голосования"""
    return contract.functions.getOptions(topic_id).call()

def vote_for_topic(topic_id: int, option: str, user_uuid) -> str:
    """Голосует за вариант в топике"""
    account = w3.eth.account.from_key(os.getenv("OWNER_PRIVATE_KEY"))

    tx = contract.functions.vote(topic_id, option, user_uuid).build_transaction({
        'chainId': 1337,
        'gas': 200000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return tx_hash.hex()

def get_vote_count(topic_id: int, option: str) -> int:
    """Получает количество голосов за вариант в топике"""
    return contract.functions.getVotes(topic_id, option).call()

print(create_vote_topic("Тестовый топик 2", ["Вариант 1", "Вариант 2"]))
print(get_topic_details(1))  # Получаем детали топика с ID 0
print(vote_for_topic(1, "Вариант 2", "test_uuid".encode('utf-8')))
print(get_vote_count(1, "Вариант 2"))  # Получаем количество голосов за "Вариант 1"