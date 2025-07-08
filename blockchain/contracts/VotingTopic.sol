// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VotingManager
 * @notice Управляет множественными темами голосования в одном контракте
 */
contract VotingManager {
    // Структура темы
    struct Topic {
        string title;          // Заголовок темы
        string[] options;      // Варианты голосования
        bool exists;           // Флаг существования темы
    }

    // Автоинкрементный ID для новых тем
    uint256 public nextTopicId;

    // Хранит все темы по их ID
    mapping(uint256 => Topic) private topics;

    // Голоса: topicId => option => count
    mapping(uint256 => mapping(string => uint256)) private votes;

    // Статус участия: topicId => адрес => проголосовал ли
    mapping(uint256 => mapping(address => bool)) private hasVoted;

    /**
     * @notice Создаёт новую тему голосования
     * @param _title Заголовок темы
     * @param _options Массив вариантов (минимум 2)
     */
    function createTopic(string memory _title, string[] memory _options) external {
        require(_options.length >= 2, "Нужно минимум два варианта");

        uint256 topicId = nextTopicId;
        Topic storage t = topics[topicId];
        t.title = _title;
        t.exists = true;
        
        for (uint i = 0; i < _options.length; i++) {
            t.options.push(_options[i]);
            votes[topicId][_options[i]] = 0;
        }

        nextTopicId++;
    }

    /**
     * @notice Голосует за указанный вариант в теме
     * @param topicId ID темы
     * @param option Вариант, за который голосуют
     */
    function vote(uint256 topicId, string memory option) external {
        require(topics[topicId].exists, "Тема не найдена");
        require(!hasVoted[topicId][msg.sender], "Уже голосовали");
        require(_validOption(topicId, option), "Недопустимый вариант");

        votes[topicId][option]++;
        hasVoted[topicId][msg.sender] = true;
    }

    /**
     * @notice Получить все варианты темы
     * @param topicId ID темы
     * @return Массив вариантов
     */
    function getOptions(uint256 topicId) external view returns (string[] memory) {
        require(topics[topicId].exists, "Тема не найдена");
        return topics[topicId].options;
    }

    /**
     * @notice Получить число голосов за вариант
     * @param topicId ID темы
     * @param option Вариант
     * @return Количество голосов
     */
    function getVotes(uint256 topicId, string memory option) external view returns (uint256) {
        require(topics[topicId].exists, "Тема не найдена");
        return votes[topicId][option];
    }

    /**
     * @dev Проверяет допустимость варианта для темы
     */
    function _validOption(uint256 topicId, string memory option) internal view returns (bool) {
        string[] storage opts = topics[topicId].options;
        for (uint i = 0; i < opts.length; i++) {
            if (keccak256(bytes(opts[i])) == keccak256(bytes(option))) {
                return true;
            }
        }
        return false;
    }
}  
