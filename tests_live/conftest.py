# pylint: disable=redefined-outer-name
import pytest
from scripts.utils.get_proxied_implementation import get_proxied_implementation

USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
CRV3CRYPTO_ADDRESS = "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff"


@pytest.fixture(scope="session")
def yearn_lib(pm):
    yield pm('yearn/yearn-vaults@0.4.3')


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def user(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def random_address(accounts):
    yield accounts[3]


@pytest.fixture(
    scope="module",
    params=[USDC_ADDRESS, CRV3CRYPTO_ADDRESS],
    ids=["usdc", "crv3crypto"])
def token(yearn_lib, request):
    yield yearn_lib.Token.at(request.param)


@pytest.fixture(scope="module")
def vault(yearn_lib, registry, token):
    vault_address = registry.latestVault(token)
    yield yearn_lib.Vault.at(vault_address)


@pytest.fixture(scope="module")
def vaults(token, yearn_router, registry):
    num_vaults = yearn_router.numVaults(token)
    vault_addresses = []
    for vault_id in range(num_vaults):
        vault_addresses.append(registry.vaults(token, vault_id))
    yield vault_addresses


@pytest.fixture(scope="module")
def registry(yearn_lib):
    yield yearn_lib.Registry.at("v2.registry.ychad.eth")


@pytest.fixture(scope="module")
def gov(registry, accounts):
    yield accounts.at(registry.governance(), force=True)


@pytest.fixture(scope="module")
def create_registry(yearn_lib, gov):
    def _create_registry():
        return gov.deploy(yearn_lib.Registry)

    yield _create_registry


@pytest.fixture(scope="module")
def proxy_admin(owner, UtilProxyAdmin):
    return owner.deploy(UtilProxyAdmin)


@pytest.fixture(scope="module")
def implementation(owner, YearnRouter):
    yield owner.deploy(YearnRouter)


@pytest.fixture(scope="module")
def proxy(owner, implementation, proxy_admin, registry, UtilProxy):
    initializer = implementation.initialize.encode_input(registry)
    return owner.deploy(UtilProxy, implementation, proxy_admin, initializer)


@pytest.fixture(scope="module")
def yearn_router(YearnRouter, proxy):
    return get_proxied_implementation(YearnRouter, proxy.address)


# Autouse fixtures


@pytest.fixture(scope="module", autouse=True)
def mint_usdc(Contract, user, accounts):
    _token = Contract.from_explorer(USDC_ADDRESS)

    master_minter = accounts.at(_token.masterMinter(), force=True)
    _token.configureMinter(user, 10000, {"from": master_minter})
    _token.mint(user, 10000, {"from": user})


@pytest.fixture(scope="module", autouse=True)
def mint_crv3crypto(Contract, user, accounts):
    _token = Contract.from_explorer(CRV3CRYPTO_ADDRESS)
    minter = accounts.at(_token.minter(), force=True)
    _token.mint(user, 10000, {"from": minter})


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
