// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingNotary {
    // 1. Владелец контракта
    address public owner;
    
    // 2. Хранилище записей
    mapping(string => string) public records;
    
    // 3. Событие для логгирования
    event VoteRecorded(string indexed voteId, string resultHash);
    
    // 4. Конструктор
    constructor() {
        owner = msg.sender;
    }
    
    // 5. Функция записи результатов
    function recordVote(string memory voteId, string memory resultHash) external {
        // Проверка прав
        require(msg.sender == owner, "Only owner can record votes");
        
        // Проверка, что запись не существует
        require(bytes(records[voteId]).length == 0, "Vote already recorded");
        
        // Сохранение записи
        records[voteId] = resultHash;
        
        // Генерация события
        emit VoteRecorded(voteId, resultHash);
    }
    
    // 6. Функция чтения
    function getRecord(string memory voteId) external view returns(string memory) {
        return records[voteId];
    }
}