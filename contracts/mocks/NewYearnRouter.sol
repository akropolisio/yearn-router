// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.13;

import "../YearnRouter.sol";

contract NewYearnRouter is YearnRouter {
    uint256 public newVariable;

    function setNewVariable(uint256 _newVariable) external {
        newVariable = _newVariable;
    }
}
