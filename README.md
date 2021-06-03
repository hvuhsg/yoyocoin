# yoyocoin
PoS blockchain python (but a bit different)  

[![Build Status](https://travis-ci.com/hvuhsg/yoyocoin.svg?branch=main)](https://travis-ci.com/hvuhsg/yoyocoin)  

#### Explanation
This coin will use PoS to determine witch wallet has won and can forge the next block (incentive: get the fee's)

##### PoS mechanism
**The wallet with the most score win and can forge the next block**,
in the time period of the block creation every wallet who have more then X score can forge the next block, every node select the one with the highest score.

If node receive block that is more than 2 blocks old (Example: current block index 20, old block index < 18)
the block add punishment data to the transaction pull (the punishment data must contain valid block signature)
the punished node __block count__ is reset.
```python
import math
def _calculate_forger_score(self, forger_wallet):
    MAX_BLOCKS_FOR_SCORE = 200
    current_block_index = self.length
    blocks_number = min((current_block_index - forger_wallet["last_transaction"]), MAX_BLOCKS_FOR_SCORE)
    multiplier = (blocks_number**math.e)/(111**math.e)+0.0000000001
    return forger_wallet["balance"] * multiplier
```

#### code parts
| Name          | Description                                          |
| ------------- | ---------------------------------------------------- |
| node          | coin p2p network client and server                   |
| blockchain    | manage chain + block foreign + maintaining consensus |

