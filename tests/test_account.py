import pytest


# scope ="module"|"function"|"class"|"session"
@pytest.fixture
def token(Token, accounts):
    return accounts[0].deploy(Token, 'Test Token', 'TST', 18, 1000)


@pytest.fixture
def distribute_tokens(token, accounts):
    for i in range(1, 10):
        token.transfer(accounts[i], 100, {'from': accounts[0]})


def test_account_balance(accounts):
    balance = accounts[0].balance()
    accounts[0].transfer(accounts[1], "10 ether", gas_price=0)

    assert balance - "10 ether" == accounts[0].balance()


def test_transer(token, accounts):
    token.transfer(accounts[1], 100, {'from': accounts[0]})
    assert token.balanceOf(accounts[0]) == 900


@pytest.fixture(scope="module", autouse=True)
def shared_setup(module_isolation):
    pass
