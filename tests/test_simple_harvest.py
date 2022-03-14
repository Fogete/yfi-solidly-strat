import brownie
from brownie import Contract
from brownie import config
import math


def test_simple_harvest(gov,
    token,
    vault,
    strategist,
    whale,
    strategy,
    chain,
    woofy_filled_swapper,
    strategist_ms,
    sex,
    solid,
    woofy,
    yfi,
    yfi_woofy_lp,
    amount,
    accounts):
    assert woofy.balanceOf(woofy_filled_swapper) > 0

    ## deposit to the vault after approving
    aidrop = 0.1*1e18
    startingWhale = token.balanceOf(whale)-aidrop
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    newWhale = token.balanceOf(whale)

    print(yfi.balanceOf(yfi_woofy_lp))
    print(woofy.balanceOf(yfi_woofy_lp))
    print(strategy.neededToArbPeg())

    # harvest, store asset amount
    chain.sleep(1)
    strategy.setDoHealthCheck(False, {"from": gov})
    strategy.harvest({"from": gov})

    print(yfi.balanceOf(yfi_woofy_lp))
    print(woofy.balanceOf(yfi_woofy_lp))
    print(strategy.neededToArbPeg())

    
    print(yfi.balanceOf(strategy))
    print(woofy.balanceOf(strategy))
    chain.sleep(1)
    old_assets = vault.totalAssets()
    assert old_assets > 0
    assert token.balanceOf(strategy) < 1e12 
    assert strategy.estimatedTotalAssets() > 0
    print("\nStarting vault total assets: ", old_assets / (10 ** token.decimals()))

    # simulate 12 hours of earnings
    chain.sleep(43200)
    chain.mine(1)


    token.transfer(vault, aidrop, {"from": whale})
    

    # harvest, store new asset amount. Turn off health check since we are only ones in this pool.
    chain.sleep(1)
    strategy.setDoHealthCheck(False, {"from": gov})
    strategy.harvest({"from": gov})

    assert sex.balanceOf(strategy) > 0
    assert solid.balanceOf(strategy) > 0
    chain.sleep(1)

    new_assets = vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    assert new_assets >= old_assets
    print(
        "\nVault total assets after 1 harvest: ", new_assets / (10 ** token.decimals())
    )

    # Display estimated APR
    print(
        "\nEstimated APR: ",
        "{:.2%}".format(
            ((new_assets - old_assets) * (365 * 2)) / (strategy.estimatedTotalAssets())
        ),
    )
    apr = ((new_assets - old_assets) * (365 * 2)) / (strategy.estimatedTotalAssets())
    assert apr > 0

    print(strategy.balanceOfLPStaked()/1e18)
    # withdraw and confirm we made money, or at least that we have about the same
    vault.withdraw({"from": whale})
    print(vault.totalDebt())
    assert token.balanceOf(whale) >= startingWhale
