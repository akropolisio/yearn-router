import pytest

import brownie


@pytest.fixture
def token(Token, accounts):
    return accounts[0].deploy(Token, 'Test Token', 'TST', 18, 1000)


def test_transfer_reverts(accounts, Token):
    token = accounts[0].deploy(Token, "Test Token", "TST", 18, 1e23)
    with brownie.reverts('Insufficient balance'):
        token.transfer(accounts[1], 1e24, {'from': accounts[0]})


@pytest.mark.parametrize('amount', [0, 100, 500])
def test_transferFrom_reverts(token, accounts, amount):
    token.approve(accounts[1], amount, {'from': accounts[0]})
    assert token.allowance(accounts[0], accounts[1]) == amount
