from blockchain.utils import record_vote, get_vote_record
import hashlib
import json

# Тестовые данные
vote_data = {
    "vote_id": "test_vote_1",
    "results": {"yes": 15, "no": 5}
}

# Конвертируем в JSON и хешируем
results_str = json.dumps(vote_data["results"], sort_keys=True)
result_hash = hashlib.sha256(results_str.encode()).hexdigest()

print("Отправляем транзакцию в блокчейн...")
tx_hash = record_vote(vote_data["vote_id"], result_hash)
print(f"Транзакция отправлена! Хеш: {tx_hash}")
print(f"Ссылка: https://mumbai.polygonscan.com/tx/{tx_hash}")

print("\nЧитаем данные из блокчейна...")
record = get_vote_record(vote_data["vote_id"])
print(f"Запись в блокчейне: {record}")