import brownie
import pytest


def test_deployment(live_yearn_router, live_proxied_router, live_proxy_admin, live_proxy, live_registry):
    assert live_proxy_admin.getProxyAdmin(live_proxy) == live_proxy_admin
    assert live_proxy_admin.getProxyImplementation(
        live_proxy) == live_yearn_router
    assert live_proxied_router.registry() == live_registry


def test_transferOwnership(owner, random_address, live_proxied_router, live_proxy_admin):
    assert live_proxied_router.owner() == owner
    assert live_proxy_admin.owner() == owner

    live_proxied_router.transferOwnership(random_address, {"from": owner})
    live_proxy_admin.transferOwnership(random_address, {"from": owner})
    assert live_proxied_router.owner() == random_address
    assert live_proxy_admin.owner() == random_address


def test_change_proxy_admin(owner, random_address, live_proxy_admin, live_proxy, UtilProxyAdmin):
    new_admin = owner.deploy(UtilProxyAdmin)

    with brownie.reverts():
        live_proxy_admin.changeProxyAdmin(
            live_proxy, new_admin, {"from": random_address})

    live_proxy_admin.changeProxyAdmin(live_proxy, new_admin, {"from": owner})
    assert new_admin.getProxyAdmin(live_proxy) == new_admin

    with brownie.reverts():
        live_proxy.changeAdmin(owner, {"from": owner})
        live_proxy_admin.getProxyAdmin(live_proxy)


def test_upgrade(owner, random_address, live_registry, live_proxy_admin, live_proxy, YearnRouter, NewYearnRouter):
    new_implementation = owner.deploy(NewYearnRouter)
    new_implementation.initialize(live_registry)
    new_implementation.setNewVariable("22")

    with brownie.reverts():
        live_proxy_admin.upgrade(live_proxy, new_implementation, {
                                 "from": random_address})
        live_proxy.upgradeTo(new_implementation, {"from": owner})

    live_proxy_admin.upgrade(live_proxy, new_implementation, {"from": owner})

    YearnRouter.remove(live_proxy)
    new_proxied_router = NewYearnRouter.at(live_proxy)

    assert live_proxy_admin.getProxyImplementation(
        live_proxy) == new_implementation
    assert new_proxied_router.newVariable() == "0"


def test_upgradeAndCall(owner, random_address, live_registry, live_proxy_admin, live_proxy, NewYearnRouter):
    new_implementation = owner.deploy(NewYearnRouter)
    new_implementation.initialize(live_registry)
    new_implementation.setNewVariable("22")

    set_new_variable_call = new_implementation.setNewVariable.encode_input(
        "12")

    with brownie.reverts():
        live_proxy_admin.upgradeAndCall(
            live_proxy, new_implementation, set_new_variable_call, {"from": random_address})
        live_proxy.upgradeToAndCall(
            new_implementation, set_new_variable_call, {"from": owner})

    live_proxy_admin.upgradeAndCall(
        live_proxy, new_implementation, set_new_variable_call, {"from": owner})

    new_proxied_router = NewYearnRouter.at(live_proxy)

    assert live_proxy_admin.getProxyImplementation(
        live_proxy) == new_implementation
    assert new_proxied_router.registry() == live_registry
    assert new_proxied_router.newVariable() == "12"
