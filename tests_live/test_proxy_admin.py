import brownie
import pytest

from scripts.utils.get_proxied_implementation import get_proxied_implementation


def test_deployment(yearn_router, proxied_router, proxy_admin, proxy, registry):
    assert proxy_admin.getProxyAdmin(proxy) == proxy_admin
    assert proxy_admin.getProxyImplementation(
        proxy) == yearn_router
    assert proxied_router.registry() == registry


def test_transferOwnership(owner, random_address, proxied_router, proxy_admin):
    assert proxied_router.owner() == owner
    assert proxy_admin.owner() == owner

    proxied_router.transferOwnership(random_address, {"from": owner})
    proxy_admin.transferOwnership(random_address, {"from": owner})
    assert proxied_router.owner() == random_address
    assert proxy_admin.owner() == random_address


def test_change_proxy_admin(owner, random_address, proxy_admin, proxy, UtilProxyAdmin):
    new_admin = owner.deploy(UtilProxyAdmin)

    with brownie.reverts():
        proxy_admin.changeProxyAdmin(
            proxy, new_admin, {"from": random_address})

    proxy_admin.changeProxyAdmin(proxy, new_admin, {"from": owner})
    assert new_admin.getProxyAdmin(proxy) == new_admin

    with brownie.reverts():
        proxy.changeAdmin(owner, {"from": owner})

    with brownie.reverts():
        proxy_admin.getProxyAdmin(proxy)


def test_upgrade(owner, random_address, registry, proxy_admin, proxy, NewYearnRouter):
    new_implementation = owner.deploy(NewYearnRouter)
    new_implementation.initialize(registry)
    new_implementation.setNewVariable("22")

    with brownie.reverts():
        proxy_admin.upgrade(proxy, new_implementation, {
            "from": random_address})

    with brownie.reverts():
        proxy.upgradeTo(new_implementation, {"from": owner})

    proxy_admin.upgrade(proxy, new_implementation, {"from": owner})

    new_proxied_router = get_proxied_implementation(
        NewYearnRouter, "NewYearnRouter", proxy.address)

    assert proxy_admin.getProxyImplementation(
        proxy) == new_implementation
    assert new_proxied_router.newVariable() == "0"


def test_upgradeAndCall(owner, random_address, registry, proxy_admin, proxy, NewYearnRouter):
    new_implementation = owner.deploy(NewYearnRouter)
    new_implementation.initialize(registry)
    new_implementation.setNewVariable("22")

    set_new_variable_call = new_implementation.setNewVariable.encode_input(
        "12")

    with brownie.reverts():
        proxy_admin.upgradeAndCall(
            proxy, new_implementation, set_new_variable_call, {"from": random_address})

    with brownie.reverts():
        proxy.upgradeToAndCall(
            new_implementation, set_new_variable_call, {"from": owner})

    proxy_admin.upgradeAndCall(
        proxy, new_implementation, set_new_variable_call, {"from": owner})

    new_proxied_router = get_proxied_implementation(
        NewYearnRouter, "NewYearnRouter", proxy.address)

    assert proxy_admin.getProxyImplementation(
        proxy) == new_implementation
    assert new_proxied_router.registry() == registry
    assert new_proxied_router.newVariable() == "12"
