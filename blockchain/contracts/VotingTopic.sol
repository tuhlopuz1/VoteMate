// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingManager {
    struct Topic {
        string title;
        string[] options;
        bool exists;
    }
    event TopicCreated(uint256 indexed topicId, string title);

    uint256 public nextTopicId;
    mapping(uint256 => Topic) private topics;
    mapping(uint256 => mapping(string => uint256)) private votes;
    mapping(uint256 => mapping(bytes32 => bool)) private hasVotedByUUID;

    function createTopic(string memory _title, string[] memory _options) external returns (uint256) {
        require(_options.length >= 2, "Minimum 2 variants required");

        uint256 topicId = nextTopicId;
        Topic storage t = topics[topicId];
        t.title = _title;
        t.exists = true;
        
        for (uint i = 0; i < _options.length; i++) {
            t.options.push(_options[i]);
            votes[topicId][_options[i]] = 0;
        }

        nextTopicId++;
        emit TopicCreated(topicId, _title);
        return topicId;
    }

    // ДОБАВЛЕНО: параметр bytes32 uuid для идентификации пользователя
    function vote(uint256 topicId, string memory option, bytes32 uuid) external {
        require(topics[topicId].exists, "Topic not found");
        require(uuid != 0, "Invalid UUID"); // Проверка нулевого UUID
        require(!hasVotedByUUID[topicId][uuid], "Already voted for this topic");
        require(_validOption(topicId, option), "Invalid option");

        votes[topicId][option]++;
        hasVotedByUUID[topicId][uuid] = true; // Фиксируем голосование
    }

    function getOptions(uint256 topicId) external view returns (string[] memory) {
        require(topics[topicId].exists, "Topic not found");
        return topics[topicId].options;
    }

    function getVotes(uint256 topicId, string memory option) external view returns (uint256) {
        require(topics[topicId].exists, "Topic not found");
        return votes[topicId][option];
    }

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