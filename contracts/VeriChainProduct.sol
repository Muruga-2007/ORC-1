// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract VeriChainProduct is ERC721, AccessControl {
    bytes32 public constant BRAND_ROLE = keccak256("BRAND_ROLE");

    // fpHash -> tokenId (tokenId is uint256(fpHash))
    mapping(bytes32 => uint256) public fpToToken;
    mapping(uint256 => bytes32) public tokenToFp;
    mapping(uint256 => bytes32) public tokenMetaHash;

    event ProductMinted(uint256 indexed tokenId, bytes32 indexed fpHash, address indexed to);
    event ProductMetaSet(uint256 indexed tokenId, bytes32 metaHash);

    constructor(address brandAdmin) ERC721("VeriChain Product", "VCP") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(BRAND_ROLE, brandAdmin);
    }

    function mintWithFingerprint(bytes32 fpHash, address to) external onlyRole(BRAND_ROLE) returns (uint256) {
        require(fpToToken[fpHash] == 0, "Fingerprint already minted");

        uint256 tokenId = uint256(fpHash);
        // Simplified check as _exists is removed in newer ERC721 or handled differently
        // In OpenZeppelin 5.x, use _ownerOf or similar if needed, or just let mint fail if exists.
        
        fpToToken[fpHash] = tokenId;
        tokenToFp[tokenId] = fpHash;

        _safeMint(to, tokenId);

        emit ProductMinted(tokenId, fpHash, to);
        return tokenId;
    }

    function setProductMeta(uint256 tokenId, bytes32 metaHash) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner"); // Simple compatibility check
        tokenMetaHash[tokenId] = metaHash;
        emit ProductMetaSet(tokenId, metaHash);
    }

    // Explicitly handle supportsInterface due to AccessControl & ERC721
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
