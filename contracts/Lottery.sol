// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {
    enum LotteryState {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    uint256 public entranceFee;
    address payable[] public players;
    address payable public winner;
    LotteryState public lotteryState;

    uint256 public fee;
    bytes32 public keyHash;
    uint256 randomNumber;
    AggregatorV3Interface internal priceFeed;
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address priceFeedAddress,
        address myVRFCoordinatorAddress,
        address linkTokenAddress,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(myVRFCoordinatorAddress, linkTokenAddress) {
        lotteryState = LotteryState.CLOSED;
        entranceFee = 50 * (10**18);
        priceFeed = AggregatorV3Interface(priceFeedAddress);
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(
            lotteryState == LotteryState.OPEN,
            "The Lottery is not opened yet!!"
        );
        require(msg.value >= getEntranceFee(), "Not enough eth");

        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        // to wei
        uint256 adjectedPrice = uint256(price) * 10**10;
        uint256 costToEnter = (entranceFee * (10**18)) / adjectedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lotteryState == LotteryState.CLOSED,
            "The Lottery is already opened!!"
        );

        lotteryState = LotteryState.OPEN;
    }

    function endLottery() public onlyOwner {
        require(
            lotteryState == LotteryState.OPEN,
            "The Lottery is already closed!!"
        );
        lotteryState = LotteryState.CALCULATING_WINNER;

        // winner_index = uint256(
        //     keccack256(
        //         abi.encodePacked(
        //             nonce,
        //             msg.sender,
        //             block.difficulty,
        //             block.timestamp
        //         )
        //     )
        // ) % players.length;

        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness)
        internal
        override
    {
        require(
            lotteryState == LotteryState.CALCULATING_WINNER,
            "You are not there yet"
        );

        require(randomness > 0, "random number is not here");
        uint256 indexOfWinner = randomness % players.length;
        winner = players[indexOfWinner];
        winner.transfer(address(this).balance);

        players = new address payable[](0);
        lotteryState = LotteryState.CLOSED;
        randomNumber = randomness;
    }
}
