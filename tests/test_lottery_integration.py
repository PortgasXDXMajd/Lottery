from brownie import Lottery, config, network, exceptions
from scripts.helper import (
    LOCAL_BLOCKCHAIN_ENVIR,
    get_account,
    fund_with_link,
    get_contract,
)
from web3 import Web3
from scripts.deploy import deploy_lottery
from web3 import Web3
import pytest


def test_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    fund_with_link(lottery.address)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]

    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, 777, lottery.address, {"from": account}
    )

    assert lottery.winner() == account
    assert lottery.balance() == 0
