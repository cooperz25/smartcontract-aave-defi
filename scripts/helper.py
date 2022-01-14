from brownie import (
    accounts,
    network,
    config,
    Contract,
)


DEV_NETWORK = ["development", "gananche-local"]
MAINNET_FORK = ["mainnet-fork-dev", "mainnet-fork-dev2"]


def getAccount(index=None, networkId=None):
    if network.show_active() in DEV_NETWORK or network.show_active() in MAINNET_FORK:
        if index:
            return accounts[index]
        if networkId:
            return accounts.load(networkId)
        return accounts[0]

    # default
    return accounts.add(config["wallets"]["key"])


def getIsPublish(_networkName):
    if (
        _networkName in DEV_NETWORK
        or _networkName in MAINNET_FORK
        or _networkName == "kovan"
    ):
        return False
    else:
        return True
