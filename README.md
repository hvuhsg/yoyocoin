# yoyocoin
PoS blockchain python (but a bit different)  

[![Build Status](https://travis-ci.com/hvuhsg/yoyocoin.svg?branch=main)](https://travis-ci.com/hvuhsg/yoyocoin)  

#### Explanation
This coin will use PoS to determine witch wallet has won the lottery and can forge the next block (and get the fee's)

The lottery function gets hash 256 bit as input and outputs number (float) in range of 0-1000.
it's uses the hash of the previous block

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

The wallet with the smallest score that have more then 100 coins wins and can forge then new block.


#### code parts
Colons can be used to align columns.

| Name          | Description                                          |
| ------------- |:----------------------------------------------------:|
| server        | listen to transactions and blocks                    |
| blockchain    | manage chain + block foreign + maintaining consensus |
| client        | menage p2p network                                   |

