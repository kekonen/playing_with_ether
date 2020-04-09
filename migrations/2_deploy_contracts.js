const ToDoList = artifacts.require("./ToDoList.sol");
const Coin = artifacts.require("./Coin.sol");

module.exports = function(deployer) {
  deployer.deploy(ToDoList);
  deployer.deploy(Coin);
};
