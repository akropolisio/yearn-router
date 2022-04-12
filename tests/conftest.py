import pytest
from brownie import Contract


@pytest.fixture(scope="session")
def yearn_vaults(pm):
    yield pm('yearn/yearn-vaults@0.4.3')


@pytest.fixture
def gov(accounts):
    yield accounts[0]


@pytest.fixture
def affiliate(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[2]


@pytest.fixture
def rewards(accounts):
    yield accounts[3]


@pytest.fixture
def rando(accounts):
    yield accounts[3]


@pytest.fixture
def rando2(accounts):
    yield accounts[4]


@pytest.fixture
def token(yearn_vaults, gov):
    yield gov.deploy(yearn_vaults.Token, 18)


@pytest.fixture
def shape_shift_router(affiliate, registry, YearnRouter):
    yield affiliate.deploy(
        YearnRouter,
        registry
    )


@pytest.fixture
def vault(create_vault, token):
    yield create_vault(token=token)


@pytest.fixture
def create_vault(yearn_vaults, live_registry, gov, rewards, guardian):
    def create_vault(token, releaseDelta=0, governance=gov):
        tx = live_registry.newExperimentalVault(
            token,
            governance,
            guardian,
            rewards,
            "vault",
            "token",
            releaseDelta,
            {"from": governance},
        )
        vault = yearn_vaults.Vault.at(tx.return_value)

        vault.setDepositLimit(2 ** 256 - 1, {"from": governance})
        return vault

    yield create_vault


@pytest.fixture
def registry(yearn_vaults, gov):
    yield gov.deploy(yearn_vaults.Registry)


@pytest.fixture
def new_registry(yearn_vaults, gov):
    yield gov.deploy(yearn_vaults.Registry)


@pytest.fixture
def live_token(live_vault):
    # this will be the address of the Curve LP token
    token_address = live_vault.token()
    yield Contract(token_address)


@pytest.fixture
def live_vault(yearn_vaults):
    # yvseth
    yield yearn_vaults.Vault.at("0x986b4aff588a109c09b50a03f42e4110e29d353f")


@pytest.fixture
def live_shape_shift_router(ShapeShiftDAORouter, affiliate, live_registry):
    yield affiliate.deploy(
        ShapeShiftDAORouter,
        live_registry
    )


@pytest.fixture
def live_registry(yearn_vaults):
    yield yearn_vaults.Registry.at("v2.registry.ychad.eth")


@pytest.fixture
def live_whale(accounts):
    whale = accounts.at(
        "0x3c0ffff15ea30c35d7a85b85c0782d6c94e1d238", force=True
    )  # make sure this address holds big bags of want()
    yield whale


@pytest.fixture
def live_gov(live_registry, accounts):
    yield accounts.at(live_registry.governance(), force=True)
