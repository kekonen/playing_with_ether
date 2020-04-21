const ToDoList = artifacts.require("./ToDoList.sol");
const Coin = artifacts.require("./Coin.sol");
const CoinFlip = artifacts.require("./CoinFlip.sol");

module.exports = function(deployer) {
  deployer.deploy(ToDoList);
  deployer.deploy(Coin);
  deployer.deploy(CoinFlip);
};
