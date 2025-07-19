// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BQPD {
    //Phase 1
    struct Entity {
        string uid;
        string entityType;
        address publicKey;
        bool isRegistered;
    }

    mapping(address => Entity) public registeredEntities;

    event EntityRegistered(address indexed addr, string uid, string entityType);

    function registerEntity(string memory _uid, string memory _entityType) public {
        require(!registeredEntities[msg.sender].isRegistered, "Entity already registered");
        require(
            keccak256(bytes(_entityType)) == keccak256("PS") || 
            keccak256(bytes(_entityType)) == keccak256("ECC") ||
            keccak256(bytes(_entityType)) == keccak256("TA"),
            "Invalid Entity Type"
        );

        registeredEntities[msg.sender] = Entity({
            uid: _uid,
            entityType: _entityType,
            publicKey: msg.sender,
            isRegistered: true
        });

        emit EntityRegistered(msg.sender, _uid, _entityType);
    }

    function getEntity(address _addr) public view returns (string memory, string memory, bool) {
        Entity memory entity = registeredEntities[_addr];
        return (entity.uid, entity.entityType, entity.isRegistered);
    }

    //Phase 2
    struct QuestionPaper {
    string ipfsHash;
    string psUid;
    address owner;
    bool isUploaded;
    }

    mapping(string => QuestionPaper) public storedQPs;

    event QPUploaded(address indexed ps, string uid, string ipfsHash);

    function storeQP(string memory _uid, string memory _ipfsHash) public {
        require(registeredEntities[msg.sender].isRegistered, "Not registered");
        require(
            keccak256(bytes(registeredEntities[msg.sender].entityType)) == keccak256(bytes("PS")),
            "Only PS can upload QP"
        );
        require(!storedQPs[_uid].isUploaded, "QP already uploaded");

        storedQPs[_uid] = QuestionPaper({
            ipfsHash: _ipfsHash,
            psUid: _uid,
            owner: msg.sender,
            isUploaded: true
        });

        emit QPUploaded(msg.sender, _uid, _ipfsHash);
    }
    
    //Phase 3
    struct ECCAccess {
    string qpUid;
    address eccAddr;
    uint256 unlockTime;
    bool isAllowed;
    }

    mapping(address => ECCAccess) public accessMap;

    event AccessGranted(address indexed ecc, string qpUid, uint256 unlockTime);

    function allowAccessToECC(string memory _qpUid, address _eccAddr, uint256 _unlockTime) public {
        require(msg.sender == taAddress, "Only TA can grant access");

        accessMap[_eccAddr] = ECCAccess({
            qpUid: _qpUid,
            eccAddr: _eccAddr,
            unlockTime: _unlockTime,
            isAllowed: true
        });

        emit AccessGranted(_eccAddr, _qpUid, _unlockTime);
    }

    function getQPForECC(address _eccAddr) public view returns (string memory, string memory) {
        ECCAccess memory access = accessMap[_eccAddr];
        require(access.isAllowed, "Access not granted");
        require(block.timestamp >= access.unlockTime, "QP not yet available");

        return (access.qpUid, storedQPs[access.qpUid].ipfsHash);
    }

}
