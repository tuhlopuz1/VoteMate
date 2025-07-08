import hashlib
import time
from typing import List, Optional

# --- Утилиты для работы со сложностью и work ---

MAX_TARGET = 0xFFFF * 2**208  # аналог Bitcoin: сложность=1

def target_to_difficulty(target: int) -> float:
    """Перевести target в human-readable difficulty."""
    return MAX_TARGET / target

def difficulty_to_target(difficulty: float) -> int:
    """Перевести difficulty обратно в target."""
    return int(MAX_TARGET / difficulty)

def calculate_work(target: int) -> float:
    """
    Work каждого блока: чем ниже target, тем больше work.
    Используем обратную пропорцию.
    """
    return MAX_TARGET / (target + 1)

# --- Класс блока ---

class Block:
    def __init__(self,
                 index: int,
                 previous_hash: str,
                 data: str,
                 timestamp: Optional[float] = None,
                 difficulty: float = 1.0):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp or time.time()
        # human-readable difficulty (например, 1.0, 1.5, 2.0…)
        self.difficulty = difficulty
        # соответствующий target
        self.target = difficulty_to_target(self.difficulty)
        self.nonce: Optional[int] = None
        self.hash: Optional[str] = None
        self.work: Optional[float] = None

    def header(self, nonce: int) -> bytes:
        return (
            str(self.index).encode() +
            self.previous_hash.encode() +
            str(self.timestamp).encode() +
            self.data.encode() +
            str(self.target).encode() +
            str(nonce).encode()
        )

    def compute_hash(self, nonce: int) -> str:
        return hashlib.sha256(self.header(nonce)).hexdigest()

    def mine(self):
        """Proof-of-Work: найти nonce, чтобы hash_int <= target."""
        nonce = 0
        while True:
            h = self.compute_hash(nonce)
            if int(h, 16) <= self.target:
                self.nonce = nonce
                self.hash = h
                self.work = calculate_work(self.target)
                return
            nonce += 1

# --- Класс цепочки ---

class Blockchain:
    def __init__(self, target_time: float = 10.0):
        self.chain: List[Block] = []
        self.chain_work: float = 0.0  # суммарная work всей цепи
        self.target_time = target_time  # желаемое время между блоками
        # создаём генезис
        genesis = Block(0, "0"*64, "Genesis", difficulty=1.0)
        genesis.mine()
        self.chain.append(genesis)
        self.chain_work = genesis.work or 0.0

    def last_block(self) -> Block:
        return self.chain[-1]

    def expected_difficulty(self, last: Block, time_elapsed: float) -> float:
        """
        Простая регулировка сложности:
         - если быстро < target/2 → +10%
         - если медленно > target*2 → –10%
         - иначе без изменений
        """
        diff = last.difficulty
        if time_elapsed < self.target_time / 2:
            return diff * 1.1
        elif time_elapsed > self.target_time * 2:
            return max(0.1, diff * 0.9)
        return diff

    def add_block(self, data: str) -> Block:
        prev = self.last_block()
        start = time.time()
        # сначала майним с текущей сложностью
        blk = Block(
            index=prev.index + 1,
            previous_hash=prev.hash,
            data=data,
            difficulty=prev.difficulty
        )
        blk.mine()
        elapsed = time.time() - start

        # проверяем, что сложность верная
        exp_diff = self.expected_difficulty(prev, elapsed)
        if abs(blk.difficulty - exp_diff) > 1e-6:
            raise ValueError("Неправильная сложность в новом блоке")

        # обновляем для следующего раунда
        blk.difficulty = exp_diff
        blk.target = difficulty_to_target(exp_diff)
        # work уже посчитана по старому target; для учебных целей допустим так

        self.chain.append(blk)
        self.chain_work += blk.work or 0.0
        print(f"Block {blk.index} mined: hash={blk.hash[:16]}…, "
f"time={elapsed:.2f}s, diff={prev.difficulty:.2f}, "
              f"cum_work={self.chain_work:.2f}")
        return blk

    def is_valid_chain(self, chain: List[Block]) -> bool:
        """Полная проверка цепочки, включая сложность и кумулятивную работу."""
        cum_work = 0.0
        for i, blk in enumerate(chain):
            # проверяем генезис
            if i == 0:
                if blk.previous_hash != "0"*64:
                    return False
                cum_work += blk.work or 0.0
                continue

            prev = chain[i-1]
            # 1) ссылка на предыдущий
            if blk.previous_hash != prev.hash:
                return False
            # 2) сам PoW
            if blk.hash != blk.compute_hash(blk.nonce):
                return False
            if int(blk.hash, 16) > blk.target:
                return False
            # 3) проверка сложности по протоколу
            dt = blk.timestamp - prev.timestamp
            exp_diff = self.expected_difficulty(prev, dt)
            if abs(blk.difficulty - exp_diff) > 1e-6:
                return False

            cum_work += blk.work or 0.0

        # можно вернуть cum_work, чтобы сравнить с другой веткой
        return True

    def replace_chain(self, new_chain: List[Block]):
        """
        Приход нового кандидата цепочки: 
        если он валиден и его cum_work > текущей, заменяем.
        """
        if not self.is_valid_chain(new_chain):
            print("Rejected: invalid chain")
            return False

        # считаем work новой цепи
        new_work = sum(b.work or 0.0 for b in new_chain)
        if new_work <= self.chain_work:
            print("Rejected: not heavier")
            return False

        # принимаем новую ветку
        self.chain = new_chain
        self.chain_work = new_work
        print("Chain replaced! New cum_work:", self.chain_work)
        return True

# --- Пример использования ---

if name == "__main__":
    bc = Blockchain(target_time=5.0)
    # честная цепь
    for i in range(3):
        bc.add_block(f"Tx {i}")

    # эмулируем атаку: подделываем последний блок
    fake = Block(
        index=bc.last_block().index + 1,
        previous_hash=bc.last_block().hash,
        data="HACKED",
        difficulty=bc.last_block().difficulty * 2  # злоумышленник завысил сложность
    )
    fake.timestamp = time.time()
    fake.mine()

    # пытаемся заменить цепь
    attacked_chain = bc.chain[:] + [fake]
    bc.replace_chain(attacked_chain)
    # → будет отклонено: «not heavier» или «invalid chain» (несоответствие сложности)