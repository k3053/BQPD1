// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract QPContract {
    struct QPData {
        string hashCode;
        uint timestamp;
    }

    mapping(string => QPData) public storedPapers;
    string[] public finalizedQPs;
    mapping(address => string) public secretKeyAssignments;

    function storeQP(string memory QPID, string memory hashCode) public returns (string memory) {
        require(bytes(storedPapers[QPID].hashCode).length == 0, "Question Paper already stored");
        storedPapers[QPID] = QPData(hashCode, block.timestamp);
        return "Question Paper stored successfully";
    }

    function finalizeQP(string memory QPID, address[] memory TA_PKs, string[] memory STA_vals) public {
        finalizedQPs.push(QPID);
        for (uint i = 0; i < TA_PKs.length; i++) {
            secretKeyAssignments[TA_PKs[i]] = STA_vals[i];
        }
    }

    function getQP(string memory QPID) public view returns (string memory, uint) {
        QPData memory data = storedPapers[QPID];
        return (data.hashCode, data.timestamp);
    }
}