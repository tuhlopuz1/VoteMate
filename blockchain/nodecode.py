import hashlib
import json
import time
from typing import List, Dict

class Block:
    def __init__(self, index: int, previous_hash: str, votes: List[Dict], timestamp=None, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.votes = votes  # список голосов
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "votes": self.votes,
            "nonce": self.nonce
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self, difficulty=3):
        self.unconfirmed_votes: List[Dict] = []
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], time.time())
        genesis_block.hash = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_vote(self, voter_id: str, candidate: str):
        vote = {
            "voter_id": voter_id,
            "candidate": candidate
        }
        self.unconfirmed_votes.append(vote)

    def mine(self):
        if not self.unconfirmed_votes:
            return False

        new_block = Block(
            index=self.last_block.index + 1,
            previous_hash=self.last_block.hash,
            votes=self.unconfirmed_votes
        )

        new_block.hash = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.unconfirmed_votes = []
        return new_block.index

    def proof_of_work(self, block: Block) -> str:
        block.nonce = 0
        computed_hash = block.compute_hash()
        target = "0" * self.difficulty
        while not computed_hash.startswith(target):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.compute_hash():
                print("Hash mismatch")
                return False
            if curr.previous_hash != prev.hash:
                print("Previous hash mismatch")
                return False
            if not curr.hash.startswith("0" * self.difficulty):
                print("Invalid proof of work")
                return False
        return True