import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_standard, install_solc, get_installable_solc_versions, set_solc_version
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def main():
    try:
        # 1. Настройка окружения
        logger.info("="*50)
        logger.info("ЗАПУСК ДЕПЛОЙ-СКРИПТА")
        logger.info("="*50)
        
        # Загрузка переменных окружения
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = "./blockchain/.env"
        load_dotenv(env_path)
        logger.info(f"Загружен .env файл: {env_path}")

        # 2. Подключение к блокчейн-ноде
        node_url = os.getenv("BLOCKCHAIN_NODE_URL")
        logger.info(f"Подключаемся к ноде: {node_url}")
        w3 = Web3(Web3.HTTPProvider(node_url))
        
        if not w3.is_connected():
            logger.error("❌ Не удалось подключиться к ноде!")
            logger.error("Проверьте URL и доступность интернета")
            return
        
        logger.info("✅ Успешное подключение к блокчейн-ноде")
        logger.info(f"ID сети: {w3.eth.chain_id}")
        logger.info(f"Последний блок: {w3.eth.block_number}")

        # 3. Проверка аккаунта
        private_key = os.getenv("OWNER_PRIVATE_KEY")
        if not private_key:
            logger.error("❌ Приватный ключ не найден в .env")
            return
        
        try:
            account = w3.eth.account.from_key(private_key)
            logger.info(f"Адрес кошелька: {account.address}")
        except ValueError as e:
            logger.error(f"❌ Неверный формат приватного ключа: {e}")
            return

        # 4. Проверка баланса
        balance = w3.eth.get_balance(account.address)
        logger.info(f"Баланс: {w3.from_wei(balance, 'ether')} MATIC")
        
        if balance < w3.to_wei(0.001, 'ether'):
            print("Доступные аккаунты:")
            for i, acc in enumerate(w3.eth.accounts):
                print(f"[{i}] {acc}, баланс: {w3.from_wei(w3.eth.get_balance(acc), 'ether')} ETH")
            logger.error("❌ Недостаточно средств для деплоя!")
            logger.error("Получите тестовые MATIC: https://faucet.polygon.technology/")
            return


        # 5. Установка компилятора
        logger.info("Устанавливаем компилятор Solidity 0.8.0...")
        available_versions = get_installable_solc_versions()
        available_versions_str = [str(v) for v in available_versions]
        if '0.8.0' not in available_versions_str:
            logger.error("Версия 0.8.0 не найдена среди доступных для установки.")
            logger.error(f"Доступные версии: {available_versions_str}")
            return
        install_solc('0.8.0')
        set_solc_version('0.8.0')
        logger.info("✅ Компилятор установлен и выбран")

        # 6. Компиляция контракта
        contract_path = os.path.join(base_dir, 'contracts', 'VotingNotary.sol')
        logger.info(f"Компилируем контракт: {contract_path}")
        
        try:
            with open(contract_path, 'r') as file:
                source_code = file.read()
                logger.debug(f"Исходный код:\n{source_code[:200]}...")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла: {e}")
            return

        try:
            compiled_sol = compile_standard({
                "language": "Solidity",
                "sources": {"VotingNotary.sol": {"content": source_code}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    }
                }
            })
            logger.info("✅ Контракт успешно скомпилирован")
        except Exception as e:
            logger.error(f"❌ Ошибка компиляции: {e}")
            return

        # 7. Подготовка к деплою
        bytecode = compiled_sol['contracts']['VotingNotary.sol']['VotingNotary']['evm']['bytecode']['object']
        abi = compiled_sol['contracts']['VotingNotary.sol']['VotingNotary']['abi']
        
        # Сохранение ABI
        abi_path = os.path.join(base_dir, 'abi.json')
        with open(abi_path, 'w') as f:
            json.dump(abi, f)
        logger.info(f"ABI сохранен в {abi_path}")

        # 8. Создание контрактного объекта
        VotingNotary = w3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = w3.eth.get_transaction_count(account.address)
        logger.info(f"Nonce: {nonce}")

        # 9. Построение транзакции
        transaction = VotingNotary.constructor().build_transaction({
            'chainId': 1337,
            'gas': 3000000,
            'gasPrice': w3.to_wei('25', 'gwei'),
            'nonce': nonce,

        })
        
        logger.info(f"Размер транзакции: {len(transaction['data'])} байт")
        estimated_gas = w3.eth.estimate_gas(transaction)
        logger.info(f"Оценка газа: {estimated_gas}")

        # 10. Подпись и отправка
        logger.info("Подписываем транзакцию...")
        signed_txn = account.sign_transaction(transaction)
        
        logger.info("Отправляем транзакцию в сеть...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        logger.info(f"Транзакция отправлена! Хеш: {tx_hash.hex()}")
        logger.info(f"Ссылка: https://mumbai.polygonscan.com/tx/{tx_hash.hex()}")

        # 11. Ожидание подтверждения
        logger.info("Ожидаем подтверждения транзакции...")
        start_time = time.time()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        logger.info(f"✅ Транзакция подтверждена за {time.time() - start_time:.2f} сек")
        logger.info(f"Блок: {tx_receipt.blockNumber}")
        logger.info(f"Использовано газа: {tx_receipt.gasUsed}")
        logger.info(f"Адрес контракта: {tx_receipt.contractAddress}")

        # 12. Сохранение адреса контракта
        with open(env_path, 'a') as env_file:
            env_file.write(f'\nCONTRACT_ADDRESS="{tx_receipt.contractAddress}"')
        logger.info(f"Адрес контракта записан в {env_path}")

        # 13. Вызов функции контракта (пример: recordVote)
        contract_instance = w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=abi
        )
        # Пример вызова функции recordVote
        vote_id = "test_vote"
        result_hash = "123"
        tx = contract_instance.functions.recordVote(vote_id, result_hash).build_transaction({
            'chainId': 1337,
            'gas': 200000,
            'gasPrice': w3.to_wei('30', 'gwei'),
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash_func = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f"Вызов recordVote отправлен! Хеш: {tx_hash_func.hex()}")

        vote_id = "test_vote"
        record = contract_instance.functions.getRecord(vote_id).call()
        logger.info(f"Результат getRecord('{vote_id}'): {record}")

        logger.info("="*50) 
        logger.info("ДЕПЛОЙ УСПЕШНО ЗАВЕРШЕН!")
        logger.info("="*50)

    except Exception as e:
        logger.exception("❌ КРИТИЧЕСКАЯ ОШИБКА:")
        raise

if __name__ == "__main__":
    main()