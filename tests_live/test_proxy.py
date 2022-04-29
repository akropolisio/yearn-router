import pytest


def test_deposit(proxied_router, token, vault, user):
    assert token.balanceOf(proxied_router) == vault.balanceOf(user) == 0

    token.approve(proxied_router, 10000, {"from": user})
    proxied_router.deposit(token, user, 10000, {"from": user})
    expectedBalance = (10000 / vault.pricePerShare()) * \
        (10**vault.decimals())

    assert vault.balanceOf(user) == expectedBalance
    assert vault.balanceOf(proxied_router) == 0
    assert token.balanceOf(proxied_router) == 0
    assert token.balanceOf(user) == 0


def test_withdraw(proxied_router, token, vault, user):
    token.approve(proxied_router, 10000, {"from": user})
    proxied_router.deposit(token, user, 10000, {"from": user})

    vault.approve(proxied_router, vault.balanceOf(user), {"from": user})
    proxied_router.withdraw(token, user, 10000, {"from": user})

    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(proxied_router) == 0
    assert token.balanceOf(proxied_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= token.balanceOf(user) <= 10000
