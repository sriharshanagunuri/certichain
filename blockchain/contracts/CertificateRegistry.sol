// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CertificateRegistry {

    struct Certificate {
        string certificateHash;
        address issuer;
        uint256 timestamp;
        bool exists;
    }

    mapping(string => Certificate) private certificates;

    function registerCertificate(
        string memory certificateId,
        string memory certificateHash
    ) public {
        certificates[certificateId] = Certificate(
            certificateHash,
            msg.sender,
            block.timestamp,
            true
        );
    }

    function getCertificate(string memory certificateId)
        public
        view
        returns (
            string memory,
            address,
            uint256,
            bool
        )
    {
        Certificate memory cert = certificates[certificateId];

        return (
            cert.certificateHash,
            cert.issuer,
            cert.timestamp,
            cert.exists
        );
    }
}