import pytest


def test_deposit(live_proxied_router, live_token, live_vault, live_vault_user, user):
    live_token.transfer(user, 10000, {"from": live_vault_user})
    assert live_token.balanceOf(
        live_proxied_router) == live_vault.balanceOf(user) == 0

    live_token.approve(live_proxied_router, 10000, {"from": user})
    live_proxied_router.deposit(live_token, user, 10000, {"from": user})
    expectedBalance = (10000 / live_vault.pricePerShare()) * \
        (10**live_vault.decimals())

    assert live_vault.balanceOf(live_proxied_router) == 0
    assert live_token.balanceOf(live_proxied_router) == 0
    assert live_token.balanceOf(user) == 0
    assert live_vault.balanceOf(user) == expectedBalance


def test_withdraw_live(live_proxied_router, live_token, live_vault, live_vault_user, user):
    live_token.transfer(user, 10000, {"from": live_vault_user})
    live_token.approve(live_proxied_router, 10000, {"from": user})
    live_proxied_router.deposit(live_token, user, 10000, {"from": user})

    live_vault.approve(live_proxied_router,
                       live_vault.balanceOf(user), {"from": user})
    live_proxied_router.withdraw(live_token, user, 10000, {"from": user})

    assert live_vault.balanceOf(user) == 0
    assert live_vault.balanceOf(live_proxied_router) == 0
    assert live_token.balanceOf(live_proxied_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(user) <= 10000
