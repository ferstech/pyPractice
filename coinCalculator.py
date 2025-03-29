print ('Change Calculator')
total = input('What is the dollar ammount >>')
#total = 1.47
while total > 0:
    if total > .25:
        quarters = total // .25
        total = total - (.25 * quarters)
        print ('Quarters', quarters)
    elif total > .10:
        dimes = total // .10
        total = total - (.10 * dimes)
        print ('Dimes', dimes)
    elif total > .05:
        nickles = total // .05
        total = total - (.05 * nickles)
        print ('Nickles', nickles)
    elif total > .01:
        penies = total // .01
        total = total - (.01 * penies)
        print ('Pennies', penies)
    else:
        break

#print (total)