# yoyocoin
PoS blockchain python (but a bit different)  

[![Build Status](https://travis-ci.com/hvuhsg/yoyocoin.svg?branch=main)](https://travis-ci.com/hvuhsg/yoyocoin)  

#### Explanation
This coin will use PoS to determine which wallet has won and can forge the next block (incentive: get the fee's, block creation is free...)


#### Running a Node

###### requirements
- docker installed
- docker-composed installed
- GIT installed
- 1 Gig RAM minimum

###### Deploying
```shell script
git clone https://github.com/hvuhsg/yoyocoin.git
cd yoyocoin
docker-compose up -d
```
The node will need to download all the history and create summary. It will take some time (depends on length and network speed)

###### Access node API
The node exposing port 6001 by default -> http://localhost:6001/docs

#### PoS mechanism
**The wallet with the most score win and can forge the next block**,
in the time period of the block creation every wallet can forge a block, every node select's the one block with the highest score.
every block have specific time frame for creation.

##### Lottery system
1. Sorted list of all the wallets is created and every wallet have a power (based on it balance and last transaction block index)
2. the node is creating sum tree from all the sorted wallets
3. random number in range of 0 - 1 is created (Working on this part)
4. the random number is multiplied with the sum tree root (sum of all)
5. the sum tree is finding the winner wallet with O(log n) time
6. the wallet score is 100 - the distance from the winner wallet (Will be changed later)

#### code parts
| Name          | Description                                          |
| ------------- | ---------------------------------------------------- |
| node          | coin p2p network client and server                   |
| blockchain    | manage chain + block foreign + maintaining consensus |
| ipfs          | IPFS go node with pubsub enabled                     |
