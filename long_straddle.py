import time
from blackscholes import black_scholes
import time
from datetime import datetime
#   >>> black_scholes(7598.45, 7000, 0.09587902546296297, 0.679, 0.03, 0.0, -1)
#   >>> black_scholes(7598.45, 9000, 0.09587902546296297, 0.675, 0.03, 0.0, 1)
from deribit_api    import RestClient
KEY     = '' #
SECRET  = ''
client = RestClient( KEY, SECRET, 'https://test.deribit.com' )
import math
from utils          import ( get_logger, lag, print_dict, print_dict_of_dicts, sort_by_key,
                             ticksize_ceil, ticksize_floor, ticksize_round )
count1 = -1
while True:
    count1 = count1 + 1
    if count1 >= 10:
        count1 = -1
        client.cancelall()
    puts = []
    calls = [] #order size * (higher of pct lim long/short * num fut) * 10 / lev
    therisk = ((250) * ((50 * 3)/100)* 10) * 1
    
    if therisk < 0:
        therisk = therisk * -1
    tty = datetime(2019,12,27).strftime('%s')

    theyield = 0.1541
    amts = {}
    spot = client.index()[ 'btc' ]
    lower = math.floor((spot - 5000) / 1000) * 1000
    higher = math.ceil((spot + 5000 ) / 1000) * 1000
    insts               = client.getinstruments()
    options        = sort_by_key( { 
        i[ 'instrumentName' ]: i for i in insts  if i[ 'kind' ] == 'option' and 'BTC' in i['instrumentName']
    } )
    exps = []
    strikes = []

    calls = []
    profits = {}
    puts = []
    es = {}
    names = []
    remember = {}
    for o in options:
        remember[options[o]['instrumentName']] = options[o]
        names.append(options[o]['instrumentName'])
        exp = datetime.strptime(options[o]['expiration'][:-13], '%Y-%m-%d')
        exps.append(exp.strftime('%s'))
        strikes.append(int(options[o]['strike']))
    a = -1
    #print(iv)
    strikes = list(dict.fromkeys(strikes))
    exps = list(dict.fromkeys(exps))
    #print(len(options))
    z = -1
    y = -1
    ivs = {}
    insts = {}
    has = {}
    lbs = {}
    optionsignore = []
    
    for o in options:
        z = z + 1
        #print(z)
        #print(client.getorderbook(options[o]['instrumentName']))
        ob = client.getorderbook(options[o]['instrumentName'])
        ivs[options[o]['instrumentName']] = ob['bidIv'] / 100
        bids = ob['bids']
        asks = ob['asks']
        la = 99
        hb = 0
        for bid in bids:
            if bid['price'] > hb:
                hb = bid['price']

        for ask in asks:
            if ask['price'] < la:
                la = ask['price']
        if hb == 0:
            optionsignore.append(options[o]['instrumentName'])
        has[options[o]['instrumentName']] = la
        lbs[options[o]['instrumentName']] = hb
        ords        = client.getopenorders( options[o]['instrumentName'] )
        expsBids = {}
        bid_ords    = [ o for o in ords ]
        for bids in bid_ords:
            ob = client.getorderbook(bids['instrument'])
            ivs[bids['instrument']] = ob['bidIv'] / 100
            bida = ob['bids']
            aska = ob['asks']
            la = 99
            hb = 0
            for bid in bida:
                if bid['price'] > hb:
                    hb = bid['price']

            for ask in aska:
                if ask['price'] < la:
                    la = ask['price']
            if bids['price'] != hb:
                client.edit( bids['orderId'], bids['quantity'] - bids['filledQuantity'], hb )
                print('edit options order for best bid!')
        positions       = client.positions()
        for option in options:
            bid_ords    = [ o for o in positions if remember[options[option]['instrumentName']]['optionType'] == 'put' and options[option]['instrumentName'] == o['instrument']  ]
            for bid in bid_ords:
                if remember[bid['instrument']] not in puts:
                    puts.append(remember[bid['instrument']])
                    amts[bid['instrument']] = bid['size']
            bid_ords    = [ o for o in positions if remember[options[option]['instrumentName']]['optionType'] == 'call' and options[option]['instrumentName'] == o['instrument']  ]
            for bid in bid_ords:
                if remember[bid['instrument']] not in calls:
                    calls.append(remember[bid['instrument']])
                    amts[bid['instrument']] = bid['size']
               
        for option in options:
            bid_ords    = [ o for o in ords if remember[options[option]['instrumentName']]['optionType'] == 'put' and options[option]['instrumentName'] == o['instrument']  ]
            for bid in bid_ords:
                if remember[bid['instrument']] not in puts:
                    puts.append(remember[bid['instrument']])
                    amts[bid['instrument']] = bid['quantity']
                
            bid_ords    = [ o for o in ords if remember[options[option]['instrumentName']]['optionType'] == 'call' and options[option]['instrumentName'] == o['instrument']  ]
            for bid in bid_ords:
                if remember[bid['instrument']] not in calls:
                    calls.append(remember[bid['instrument']])
                    amts[bid['instrument']] = bid['quantity']
                
    strikec = []
    strikep = []
    pexps = []

    for o in calls:   
        for o2 in puts:
            if o['expiration'] == o2['expiration']:

                strikec.append(int(o['strike']))
                strikep.append(int(o2['strike']))
                exp = datetime.strptime(o['expiration'][:-13], '%Y-%m-%d')
                pexps.append(exp.strftime('%s'))    
    
    abc = 0
    oldp = 0
    while abc < len(calls):
        now = time.time() 

        diff = (int(pexps[abc]) - int(now)) / 60 / 60 / 24 / 365
        p1 = black_scholes(spot, strikep[abc], diff, ivs[puts[abc]['instrumentName']], 0.03, 0.0, -1) 
        c1 = black_scholes(spot, strikec[abc], diff, ivs[calls[abc]['instrumentName']], 0.03, 0.0, 1) 
        
        c2 = black_scholes(spot * 1.11, strikep[abc], diff, ivs[puts[abc]['instrumentName']], 0.03, 0.0, -1) 
        p2 = black_scholes(spot * 1.11, strikec[abc], diff, ivs[calls[abc]['instrumentName']], 0.03, 0.0, 1) 
        c3 = black_scholes(spot * 0.89, strikep[abc], diff, ivs[puts[abc]['instrumentName']], 0.03, 0.0, -1) 
        p3 = black_scholes(spot * 0.89, strikec[abc], diff, ivs[calls[abc]['instrumentName']], 0.03, 0.0, 1) 
        cost1 =(c1 + p1)
        cost2 = (c2 + p2)
        cost3 = (c3 + p3)
        profit=(cost2-cost1)+(cost3-cost1)
        print(amts[calls[abc]['instrumentName']])  
        oldp = oldp  + spot * (has[calls[abc]['instrumentName']] * amts[calls[abc]['instrumentName']])
        #btccost / price * theprofit))
        print('therisk: ' + str(therisk))
        print('oldp: ' + str(oldp))
        therisk = therisk - oldp
        abc = abc + 1
    #therisk = therisk * 1.75    

    if therisk > 0 and therisk > 200:        
        for e in exps:
            #z = z + 1
            #print(z)
            calls = []
            puts = []
            civs = {}
            pivs = {}
            costc = []
            costp = []
            instsp = []
            instsc = []
            now = time.time() 
            if ((int(e) - int(now)) / 60 / 60 / 24 / 365 > 1 / 365 * 20):
                diff = (int(e) - int(now)) / 60 / 60 / 24 / 365

                for s in strikes:
                    a = a + 1
                    #print(a)
                    for o in options:
                        if 'BTC' in options[o]['instrumentName'] and options[o]['instrumentName'] not in optionsignore:
                            iv = ivs[options[o]['instrumentName']]
                            if iv != 0:
                                exp2 = datetime.strptime(options[o]['expiration'][:-13], '%Y-%m-%d').strftime('%s')
                                
                                if((options[o]['optionType'] == 'call' and (options[o]['strike']) == s) and (options[o]['strike']) <= higher and (options[o]['strike']) >= lower and exp2 == e):
                                    calls.append(s)
                                    #print(calls)
                                    civs[s] = iv
                                    pivs[s] = iv

                                    costc.append(has[options[o]['instrumentName']])
                                    instsc.append(options[o]['instrumentName'])

                                    
                                if((options[o]['optionType'] == 'put' and (options[o]['strike']) == s) and (options[o]['strike']) <= higher and (options[o]['strike']) >= lower and exp2 == e):
                                    
                                    puts.append(s)
                                    #print(puts)
                                    civs[s] = iv
                                    pivs[s] = iv
                                    costp.append(has[options[o]['instrumentName']])
                                    instsp.append(options[o]['instrumentName'])

            #print(len(puts))
            #print(len(calls))
            ccount = -1
            for c in calls:
                ccount = ccount+1
                pcount = -1
                for p in puts:
                    pcount = pcount + 1
                    p1 = black_scholes(spot, p, diff, pivs[p], 0.03, 0.0, -1) 
                    c1 = black_scholes(spot, c, diff, civs[c], 0.03, 0.0, 1) 
                    
                    c2 = black_scholes(spot * 1.11, p, diff, pivs[p], 0.03, 0.0, -1) 
                    p2 = black_scholes(spot * 1.11, c, diff, civs[c], 0.03, 0.0, 1) 
                    c3 = black_scholes(spot * (1-0.11), p, diff, pivs[p], 0.03, 0.0, -1) 
                    p3 = black_scholes(spot * (1-0.11), c, diff, civs[c], 0.03, 0.0, 1) 
                    cost1 =(c1 + p1)
                    cost2 = (c2 + p2)
                    cost3 = (c3 + p3)
                    profit=(cost2-cost1)+(cost3-cost1)
                    #print(profit)
                    profits[profit] = {'price': costp[pcount] + costc[ccount], 'costc': costc[ccount], 'costp': costp[pcount],'call s' : c, 'put s': p, 'call': instsc[ccount],'put': instsp[pcount],  'e': e}
                    #print(profits[profit])
                    #for pos in positions:
                        #if 'BTC' in  pos['instrument']:
                            #print(pos['floatingPl'] * 100)4

        biggest = 0
        costed = {}
        for p in profits.keys():
            costed[p] = (profits[p]['price'] * (therisk/(p+profits[p]['price'] * spot)))
            costed[p] = (therisk/p)*profits[p]['price']
            if p > biggest:
                biggest = p
        smallest = 9999999999999999
        for c in costed:
            #print(costed[c])
            if float(costed[c]) < smallest:
                smallest = float(costed[c])
                w1 = c
        try:        
            print(' ')
            print('exposure: ' + str(therisk))
            print('cost to buy: ' + str(smallest))

            print('profit per unit at +/- 5%: ' + str(w1))
            print('exposure covered: ' + str(smallest / profits[w1]['price'] * w1))
            print(profits[w1])
            #self.options[profits[w1]['call'] + profits[w1]['put']] = smallest / profits[w1]['price']
            qty = smallest / 2
            qty = qty * 10
            qty = math.ceil(qty)
            qty = qty / 10
            print(profits[w1]['put'])
            print(qty)
            print(qty, profits[w1]['costp'] )
            client.buy(profits[w1]['put'], qty, profits[w1]['costp'] )
            client.buy(profits[w1]['call'], qty, profits[w1]['costc'] )
            #self.calls.append(profits[w1]['call'])
            #self.puts.append(profits[w1]['put'])
        except Exception as e:
                e = e