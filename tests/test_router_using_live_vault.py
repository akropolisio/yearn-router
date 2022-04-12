import brownie
import pytest

from eth_account import Account

AMOUNT = 100

def test_config_live(live_token, live_vault, live_registry, live_shape_shift_router, interface):
    assert live_registry.numVaults(live_token) > 0
    assert interface.RegistryAPI(live_shape_shift_router.registry()).latestVault(live_token) == live_vault
    assert interface.RegistryAPI(live_shape_shift_router.registry()).numVaults(live_token) == 1
    assert interface.RegistryAPI(live_shape_shift_router.registry()).vaults(live_token, 0) == live_vault
    assert live_shape_shift_router.latestVault(live_token) == live_vault
    assert live_shape_shift_router.numVaults(live_token) == 1
    assert live_shape_shift_router.vaults(live_token, 0) == live_vault

def test_setRegistry_live(
    rando, affiliate, live_gov, live_shape_shift_router, new_registry, gov
):
    with brownie.reverts():
        live_shape_shift_router.setRegistry(rando, {"from": rando})
    
    # Cannot set to an invalid registry
    with brownie.reverts():
        live_shape_shift_router.setRegistry(rando, {"from": affiliate})

    with brownie.reverts():
        live_shape_shift_router.setRegistry(rando, {"from": live_gov})

    # yGov must be the gov on the new registry too
    new_registry.setGovernance(rando, {"from": gov})
    new_registry.acceptGovernance({"from": rando})
    with brownie.reverts():
        live_shape_shift_router.setRegistry(new_registry, {"from": affiliate})
    new_registry.setGovernance(live_gov, {"from": rando})
    new_registry.acceptGovernance({"from": live_gov})

    live_shape_shift_router.setRegistry(new_registry, {"from": affiliate})


def test_transfer_ownership_live(rando, affiliate, live_shape_shift_router, new_registry, gov, live_gov,):
    assert live_shape_shift_router.owner() == affiliate
    new_registry.setGovernance(live_gov, {"from": gov})
    new_registry.acceptGovernance({"from": live_gov})

    with brownie.reverts():
        live_shape_shift_router.setRegistry(rando, {"from": rando})

    with brownie.reverts():
      live_shape_shift_router.transferOwnership(rando, {"from": rando})

    live_shape_shift_router.transferOwnership(rando, {"from": affiliate})

    # new owner can set registry
    assert live_shape_shift_router.owner() == rando
    live_shape_shift_router.setRegistry(new_registry, {"from": rando})


def test_deposit_live(live_token, live_vault, live_shape_shift_router, live_whale, rando):
    live_token.transfer(rando, 10000, {"from": live_whale})
    assert live_token.balanceOf(live_shape_shift_router) == live_vault.balanceOf(rando) == 0

    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})
    expectedBalance = (10000 / live_vault.pricePerShare()) * (10**live_vault.decimals())

    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(rando) == 0
    assert live_vault.balanceOf(rando) == expectedBalance

def test_deposit_with_recipient_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)

    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    expectedBalance = (10000 / live_vault.pricePerShare()) * (10**live_vault.decimals())
    live_shape_shift_router.deposit(live_token, rando2, 10000, {"from": rando})
    
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(rando) == 0
    assert live_vault.balanceOf(rando) == 0
    assert live_vault.balanceOf(rando2) == expectedBalance

def test_withdraw_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)

    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})

    live_vault.approve(live_shape_shift_router, live_vault.balanceOf(rando), {"from": rando})
    live_shape_shift_router.withdraw(live_token, rando, 10000, {"from": rando})
    
    assert live_vault.balanceOf(rando) == 0
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(rando) <= 10000

def test_withdraw_max_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)
    
    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})

    live_vault.approve(live_shape_shift_router, live_vault.balanceOf(rando), {"from": rando})
    live_shape_shift_router.withdraw(live_token, rando, {"from": rando})
    
    assert live_vault.balanceOf(rando) == 0
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(rando) <= 10000

def test_withdraw_half_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)

    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})

    live_vault.approve(live_shape_shift_router, live_vault.balanceOf(rando), {"from": rando})
    live_shape_shift_router.withdraw(live_token, rando, 5000, {"from": rando})
    
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 5000 - 10 <= live_token.balanceOf(rando) <= 5000

def test_withdraw_with_recipient_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)

    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})

    live_vault.approve(live_shape_shift_router, live_vault.balanceOf(rando), {"from": rando})
    live_shape_shift_router.withdraw(live_token, rando2, 10000, {"from": rando})
    assert live_vault.balanceOf(rando) == 0
    assert live_vault.balanceOf(rando2) == 0
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(rando2) <= 10000

def test_withdraw_half_with_recipient_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)


    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})

    live_vault.approve(live_shape_shift_router, live_vault.balanceOf(rando), {"from": rando})
    live_shape_shift_router.withdraw(live_token, rando2, 5000, {"from": rando})

    assert live_token.balanceOf(rando) == 0
    assert live_vault.balanceOf(rando2) == 0
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    
    # NOTE: Potential for tiny dust loss
    assert 5000 - 10 <= live_token.balanceOf(rando2) <= 5000

def test_withdraw_max_with_recipient_live(live_token, live_vault, live_shape_shift_router, live_whale, rando, rando2):
    clearBalances(live_token, live_vault, live_whale, rando, rando2)

    live_token.transfer(rando, 10000, {"from": live_whale})
    live_token.approve(live_shape_shift_router, 10000, {"from": rando})
    live_shape_shift_router.deposit(live_token, rando, 10000, {"from": rando})

    live_vault.approve(live_shape_shift_router, live_vault.balanceOf(rando), {"from": rando})
    live_shape_shift_router.withdraw(live_token, rando2, {"from": rando})
    assert live_vault.balanceOf(rando) == 0
    assert live_vault.balanceOf(rando2) == 0
    assert live_vault.balanceOf(live_shape_shift_router) == 0
    assert live_token.balanceOf(live_shape_shift_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(rando2) <= 10000

def clearBalances(live_token, live_vault, live_whale, rando, rando2):
  preTestBal = live_token.balanceOf(rando)
  if preTestBal > 0:
      live_token.transfer(live_whale, preTestBal, {"from": rando})
  preTestBal = live_token.balanceOf(rando2)
  if preTestBal > 0:
      live_token.transfer(live_whale, preTestBal, {"from": rando2})
  
  preTestBal = live_vault.balanceOf(rando)
  if preTestBal > 0:
      live_vault.transfer(live_whale, preTestBal, {"from": rando})
  preTestBal = live_vault.balanceOf(rando2)
  if preTestBal > 0:
      live_vault.transfer(live_whale, preTestBal, {"from": rando2})
  