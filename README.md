# Hey!


## Sign Up Here


https://www.bitmex.com/register/EJy18M (note to self: +bmex)


https://www.deribit.com/reg-4393.9303


## NOTE!


Neither Mex nor Deribit care how many accounts you have. You can only verify once, but you can have as many unverified accounts as you like. Please, if you already have a mex or deribit account, do sign up for another one with the above links. It helps the cause and the positive energy is felt for days, rest assured :) :D



## Summary


I ran a modified version of my market making bot for a day or two. 


The new strategy, in testing.py, as you may be aware, was to long and short perps and futures based on funding +/-.


Here's where the bot was after 7-8 hours. https://i.imgur.com/HFf6rxr.png


44% gains ain't nothin' to laugh at!


Afterwards, it took a bit of a dive, then eventually liquidated out as BTC grew $$ hundreds in ~1hr. https://i.imgur.com/6jMtbYs.png


The good news here is that the strategy works. There are risk factors that were too generous in this run, specifically the % of balance to have entered into long/short positions. 


there's 2 options


1. more balance, in which case 44% becomes 4.4%
2. lower pct lims, in which case 44 becomes maybe 44 maybe 20 maybe 14 but definitely not 4.44, and it wouldn't get wiped out
3. Add SL/TP


## BTC or BTC/ETH or ETH


The bot on testing.py is built on BTC+ETH balance, and will fail without it.


To run just BTC, change the def get_futures line from:


i[ 'instrumentName' ]: i for i in insts  if ('BTC-' in i['instrumentName'] or 'ETH-' in i['instrumentName'] )  and i[ 'kind' ] == 'future'#  


to:


i[ 'instrumentName' ]: i for i in insts  if ('BTC-' in i['instrumentName'] )  and i[ 'kind' ] == 'future'#  


or to run just ETH:


i[ 'instrumentName' ]: i for i in insts  if ('ETH-' in i['instrumentName'] )  and i[ 'kind' ] == 'future'#  



After serious consideration, I've added SL/TP to testing.py on Deribit!


## Settings


In bitmex-settings and deribit-settings are arrays.


Directional
0. none
1. StochRSI


Price
0. best bid/offer
1. vwap
2. BitMex Index Difference
3. BBands %B


Volatility
0. none
1. ewma
2. BBands Width
3. ATR


Quantity
0. none
1. BitMex Index Difference
2. PPO
3. Relative Volume
4. BBands %B
