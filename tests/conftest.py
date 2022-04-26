import pytest
from brownie import Contract


@pytest.fixture(scope="session")
def yearn_vaults(pm):
    yield pm('yearn/yearn-vaults@0.4.3')


@pytest.fixture(scope="session")
def gov(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def user(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def random_address(accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def random_address_2(accounts):
    yield accounts[4]


@pytest.fixture
def token(yearn_vaults, gov):
    yield gov.deploy(yearn_vaults.Token, 18)


@pytest.fixture
def yearn_router(owner, registry, YearnRouter):
    contract = owner.deploy(
        YearnRouter
    )
    contract.initialize(registry, {"from": owner})
    yield contract


@pytest.fixture
def vault(create_vault, token):
    yield create_vault(token=token)


@pytest.fixture(scope="session")
def create_vault(accounts, yearn_vaults, live_registry, gov):
    rewards = accounts.add()
    guardian = accounts.add()

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


@pytest.fixture(scope="session")
def live_token(live_vault):
    # this will be the address of the Curve LP token
    token_address = live_vault.token()
    yield Contract(token_address)


@pytest.fixture(scope="session")
def live_vault(yearn_vaults):
    # yvseth
    yield yearn_vaults.Vault.at("0x986b4aff588a109c09b50a03f42e4110e29d353f")


@pytest.fixture(scope="module", autouse=True)
def live_yearn_router(YearnRouter, owner, live_registry):
    contract = owner.deploy(
        YearnRouter,
    )
    contract.initialize(live_registry)
    yield contract


@pytest.fixture(scope="session")
def live_registry(yearn_vaults):
    yield yearn_vaults.Registry.at("v2.registry.ychad.eth")


@pytest.fixture(scope="session")
def live_vault_user(accounts):
    user = accounts.at(
        "0x3c0ffff15ea30c35d7a85b85c0782d6c94e1d238", force=True
    )  # make sure this address holds big bags of want()
    yield user


@pytest.fixture(scope="session")
def live_gov(live_registry, accounts):
    yield accounts.at(live_registry.governance(), force=True)


@pytest.fixture(scope="module", autouse=True)
def live_proxy_admin(owner, UtilProxyAdmin):
    return owner.deploy(UtilProxyAdmin)


@pytest.fixture(scope="module", autouse=True)
def live_proxy(owner, live_yearn_router, live_proxy_admin, live_registry, UtilProxy):
    initializer = live_yearn_router.initialize.encode_input(live_registry)
    return owner.deploy(UtilProxy, live_yearn_router, live_proxy_admin, initializer)


@pytest.fixture(scope="module", autouse=True)
def live_proxied_router(live_proxy, UtilProxy, YearnRouter):
    UtilProxy.remove(live_proxy)
    return YearnRouter.at(live_proxy)


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
