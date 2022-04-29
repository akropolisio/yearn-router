# pylint: disable=redefined-outer-name
from functools import lru_cache
from brownie import compile_source
import pytest


@pytest.fixture(scope="session")
def yearn_lib(pm):
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


# registry reverts new vault releases when vault apiVersions match
@pytest.fixture(scope="module")
def patch_vault_version(yearn_lib):
    # NOTE: Cache this result so as not to trigger a recompile for every version change
    @lru_cache
    def _patch_vault_version(version):
        if version is None:
            return yearn_lib.Vault
        else:
            vault_source_code = yearn_lib._sources.get("Vault")
            source = vault_source_code.replace("0.4.3", version)
            return compile_source(source).Vyper

    return _patch_vault_version


@pytest.fixture(scope="module")
def token(create_token):
    yield create_token()


@pytest.fixture(scope="module")
def create_token(yearn_lib, gov):
    def _create_token() -> yearn_lib.Token:
        return gov.deploy(yearn_lib.Token, 18)
    yield _create_token


@pytest.fixture(scope="module")
def yearn_router(owner, registry, YearnRouter):
    contract = owner.deploy(YearnRouter)
    contract.initialize(registry, {"from": owner})
    yield contract


@pytest.fixture(scope="module")
def vault(create_vault, token):
    yield create_vault(token=token, version="1.0.0")


@pytest.fixture(scope="module")
def create_vault(accounts, registry, gov, patch_vault_version):
    rewards = accounts.add()
    guardian = accounts.add()

    def _create_vault(token, version):
        _vault = patch_vault_version(version).deploy({"from": guardian})
        _vault.initialize(token, gov, rewards, "", "", guardian, gov)
        _vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
        registry.newRelease(_vault, {"from": gov})
        registry.endorseVault(_vault, {"from": gov})

        return _vault

    yield _create_vault


@pytest.fixture(scope="module")
def registry(create_registry):
    yield create_registry()


@pytest.fixture(scope="module")
def create_registry(yearn_lib, gov):
    def _create_registry():
        _registry = gov.deploy(yearn_lib.Registry)
        _vault = gov.deploy(yearn_lib.Vault)
        _registry.newRelease(_vault, {"from": gov})
        return _registry

    yield _create_registry


# Autouse fixtures


@pytest.fixture(scope="module", autouse=True)
def transfer_initial_tokens(token, user, yearn_router, gov):
    token.transfer(user, 10000, {"from": gov})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
