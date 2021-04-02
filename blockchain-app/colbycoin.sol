// Colby Coin ICO

pragma solidity ^0.4.11;

contract colbycoin_ico {
    
    // Max number of coins for sale
    uint public max_coins = 1000000;
    
    // USD to coin rate
    uint public usd_to_coin = 1000;
    
    // Total number of coins bought
    uint public total_coins_purchased = 0;
    
    // Mapping investor address to equity in coins
    mapping(address => uint) equity_coins;
    mapping(address => uint) equity_usd;
    
    // Checking if investor can buy coins
    modifier can_buy_coins(uint usd_invested) {
        require (usd_invested * usd_to_coin + total_coins_purchased <= max_coins);
        _;
    }
    
    // Get equity in coins of an investor
    function equity_in_coins(address investor) external constant returns (uint) {
        return equity_coins[investor];
    }
    
    
    // Get the equity in USD of an investor
    function equity_in_usd(address investor) external constant returns (uint) {
        return equity_usd[investor];
    }
    
    // Buying coins
    function buy_coins(address investor, uint usd_invested) external 
    can_buy_coins(usd_invested) {
        uint coins_bought = usd_invested * usd_to_coin;
        equity_coins[investor] += coins_bought;
        equity_usd[investor] = equity_coins[investor] / usd_to_coin;
        total_coins_purchased += coins_bought;
    } 
    
    // Selling Coins
    function sell_coins(address investor, uint coins_sold) external {
        equity_coins[investor] -= coins_sold;
        equity_usd[investor] = equity_coins[investor] / usd_to_coin;
        total_coins_purchased -= coins_sold;
    } 
}