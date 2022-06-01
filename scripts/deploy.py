from brownie import Lottery
from scripts.helper import (
    get_account,
    get_contract,
    get_HashKey,
    get_Fees,
    IsPublishable,
    fund_with_link,
)
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        get_Fees(),
        get_HashKey(),
        {"from": account},
        publish_source=IsPublishable(),
    )
    print("Lottery Deployed")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    trans = lottery.startLottery({"from": account})
    trans.wait(1)
    print("lottery has started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee({"from": account}) + 10000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("Entered the lottery successfully")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund contract with link token
    tx = fund_with_link(lottery.address)
    tx.wait(1)

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)

    print(f"{lottery.winner()} is the new winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
