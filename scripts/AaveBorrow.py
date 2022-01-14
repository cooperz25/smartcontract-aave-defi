from brownie import accounts, config, network, interface
from scripts import helper, swapForWETH
from web3 import Web3


def main():

    acc = helper.getAccount()

    if network.show_active() in ["mainnet-fork-dev2"]:
        swapForWETH.swap()

    lendingPool = getLendingPool()
    print(f"lending pool addr: {lendingPool}")

    print(f"approving ")
    approve(
        lendingPool.address,
        Web3.toWei(0.01, "ether"),
        config["networks"][network.show_active()]["weth"],
        acc,
    )

    # print(f"depositing...")
    # deposit(lendingPool, acc)

    print(f"getting user acc data...")
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = getUserAccountData(lendingPool, acc)

    print(
        f"avvailable borrows ETH {availableBorrowsETH} totalCollateralETH {totalCollateralETH}"
    )

    print(f"getting 50% borrow ammount")
    daiAmount = getBorrowAmmount(availableBorrowsETH, 20)
    print(f"dai amount {daiAmount}")

    print("borrowing...")
    borrow(
        lendingPool,
        acc,
        config["networks"][network.show_active()]["dai"],
        daiAmount,
        1,
        0,
        acc,
    )

    print("repaying...")
    toltalDaiAmount = getBorrowAmmount(totalDebtETH, 80)
    print(f"toltalDaiAmount {toltalDaiAmount}")
    approve(
        lendingPool.address,
        toltalDaiAmount,
        config["networks"][network.show_active()]["dai"],
        acc,
    )
    repay_all(
        lendingPool,
        config["networks"][network.show_active()]["dai"],
        toltalDaiAmount,
        1,
        acc,
    )

    print("DONE")


def repay_all(lendingPool, asset, amount, rateMode, acc):
    lendingPool.repay(asset, amount, rateMode, acc, {"from": acc})


def borrow(lendingPool, account, assetAddr, amount, irateMode, refCode, acc):
    tx = lendingPool.borrow(
        assetAddr, amount, irateMode, refCode, acc.address, {"from": account}
    )
    tx.wait(1)
    return tx


def getBorrowAmmount(availableBorrowsETH, percent):
    priceFeed = interface.IV3Aggregator(
        config["networks"][network.show_active()]["price_feed"]
    )
    _, daiPrice, _, _, _ = priceFeed.latestRoundData()
    print(f"dai price {daiPrice}")
    borrowPriceAmmountWei = (availableBorrowsETH / daiPrice) * (percent / 100)
    return Web3.toWei(borrowPriceAmmountWei, "ether")


def getUserAccountData(lendingPool, acc):
    return lendingPool.getUserAccountData(acc)


def deposit(lendingPool, acc):
    tx = lendingPool.deposit(
        config["networks"][network.show_active()]["weth"],
        Web3.toWei(0.01, "ether"),
        acc,
        0,
        {"from": acc},
    )
    tx.wait(1)
    return tx


def approve(spender, ammount, erc20addr, account):

    erc20 = interface.IERC20(erc20addr)
    result = erc20.approve(spender, ammount, {"from": account})
    return result


def getLendingPool():
    # get lending pool address provider
    lendingPoolAddrProvider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addr_provider"]
    )

    # get lending pool address
    lendingPoolAddr = lendingPoolAddrProvider.getLendingPool()
    lendingPool = interface.ILendingPool(lendingPoolAddr)
    return lendingPool
