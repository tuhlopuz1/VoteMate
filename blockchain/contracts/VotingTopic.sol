// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingManager {
    mapping(string => mapping(string => uint256)) private votes;
    event Voted(address indexed voter, string topicId, string option);
    mapping(string => mapping(address => bool)) private hasVoted;

    function vote(string memory topicId, string memory option) external {
        require(!hasVoted[topicId][msg.sender], "Already voted for this topic");

        votes[topicId][option]++;
        emit Voted(msg.sender, topicId, option); 
        hasVoted[topicId][msg.sender] = true;
    }

    function getVotes(string memory topicId, string memory option) external view returns (uint256) {
        return votes[topicId][option];
    }
}