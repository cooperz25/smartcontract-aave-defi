from brownie import accounts, config, network, interface
from scripts import helper


def main():
    swap()


def swap():
    acc = helper.getAccount()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth"])
    tx = weth.deposit({"from": acc, "value": 1 * 10 ** 17})
    tx.wait(1)
