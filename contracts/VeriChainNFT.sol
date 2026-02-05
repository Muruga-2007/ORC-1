// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract VeriChainNFT is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;
    
    // Mapping from Token ID to Document Hash
    mapping(uint256 => bytes32) public documentHashes;

    constructor() ERC721("VeriChain Certificate", "VCC") {}

    /**
     * @dev Mint a new certificate NFT.
     * @param recipient The address to receive the NFT.
     * @param docHash The SHA-256 hash of the certificate details.
     */
    function mintCertificate(address recipient, bytes32 docHash) public onlyOwner {
        uint256 tokenId = nextTokenId;
        _safeMint(recipient, tokenId);
        documentHashes[tokenId] = docHash;
        nextTokenId++;
    }

    /**
     * @dev Verify if a hash matches the one stored in a specific NFT.
     */
    function verifyHash(uint256 tokenId, bytes32 hashToVerify) public view returns (bool) {
        return documentHashes[tokenId] == hashToVerify;
    }
}
