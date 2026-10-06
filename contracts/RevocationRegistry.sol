pragma solidity ^0.8.20;

contract RevocationRegistry {
    mapping(bytes32 => bool) private revoked;
    mapping(bytes32 => uint256) private revokedAt;

    event Revoked(bytes32 indexed templateHash, uint256 timestamp);
    event Restored(bytes32 indexed templateHash, uint256 timestamp);

    function revoke(bytes32 templateHash) external {
        if (!revoked[templateHash]) {
            revoked[templateHash] = true;
            revokedAt[templateHash] = block.timestamp;
            emit Revoked(templateHash, block.timestamp);
        }
    }

    function restore(bytes32 templateHash) external {
        if (revoked[templateHash]) {
            revoked[templateHash] = false;
            emit Restored(templateHash, block.timestamp);
        }
    }

    function isRevoked(bytes32 templateHash) external view returns (bool) {
        return revoked[templateHash];
    }
}
