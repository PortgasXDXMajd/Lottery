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


def test_getting_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    print(entrance_fee)
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_cant_end_If_not_started_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.endLottery({"from": account})


def test_cant_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})
    assert lottery.lotteryState() == 2


def test_can_pick_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIR:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    fund_with_link(lottery.address)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]

    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, 777, lottery.address, {"from": account}
    )

    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    assert lottery.winner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery


def main():
    test_getting_entrance_fee()
