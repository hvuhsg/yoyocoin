# yoyocoin
PoS blockchain python (but a bit different)  

[![Build Status](https://travis-ci.com/hvuhsg/yoyocoin.svg?branch=main)](https://travis-ci.com/hvuhsg/yoyocoin)  

#### Explanation
This coin will use PoS to determine witch wallet has won the lottery and can forge the next block (and get the fee's)

The lottery function gets hash 256 bit as input and outputs number (float) in range of 0-1000.
it's uses the hash of the last block.

```python
def wallet_number(wallet_address):
    #  return number (float) in range of 0-1000
    pass

def score (wallet_address, wallet_history, lottery_number):
    #  return number (float) in range of 0-1000
    pass
```

The score algorithm return's lower number for wallet that hold more coins for more blocks (the block count stop with win of the lottery),
in addition to wallet_number distance to lottery_number.

The wallet with the smallest score that have more then 100 coins wins and can forge the new block.

<pre>
Wallet-A is the wallet number of wallet-a
Wallet-B is the wallet number of wallet-b
lottery is the number that created from the last block hash

Distance:
0                         wallet-A    lottery                       wallet-B                      1000
|                             |          |                              |                           |
|---------------------------------------------------------------------------------------------------|

wallet-power = wallet sum(coin's per block sins last win)/1000000 (million coins for 20 blocks is 2 power)
wallet-score = {wallet distance from lottery} - {wallet-power}

Power:
1000                                                     wallet-b-score      wallet-a-score          0
  |                                                            |                    |                | <- the goal
  |--------------------------------------------------------------------------------------------------|


If Wallet-A will forge new block and Wallet-B will forge new block,
the block of Wallet-A has less power so its will the chosen one in a <a href="#dispute">dispute</a>.
</pre>


#### code parts

| Name          | Description                                          |
| ------------- | ---------------------------------------------------- |
| server        | listen to transactions and blocks                    |
| blockchain    | manage chain + block foreign + maintaining consensus |
| client        | menage p2p network                                   |

