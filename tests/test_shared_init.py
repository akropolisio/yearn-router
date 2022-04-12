import pytest


@pytest.fixture(scope="module", autouse=True)
def token(Token, accounts):
    t = accounts[0].deploy(Token, "Test Token", "TST", 18, 1000)
    yield t


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_transfer(token, accounts):
    token.transfer(accounts[1], 100, {'from': accounts[0]})
    assert token.balanceOf(accounts[0]) == 900


def test_chain_reverted(token, accounts):
    assert token.balanceOf(accounts[0]) == 1000
