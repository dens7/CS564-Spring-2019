"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)


"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        for item in items:
            CategoryTable(item)
            LocationCountryTable(item)
            UserTable(item)  
            ItemTable(item)                                                          

# Category
Category = {}
def CategoryTable(item):
    global Category
    for cat in item['Category']:
        if cat not in Category: 
            Category[cat] = len(Category) + 1

# Location Country 
Country = {}
Location = {}
def LocationCountryTable(item): 
    global Country
    processSingleLocation(item)
    if item['Bids'] is None: 
        return
    for bid in item['Bids']: 
        bidder = bid['Bid']['Bidder']
        if 'Location' in bidder:
            processSingleLocation(bidder)
            
def processSingleLocation(obj):
    if "Country" in obj and obj['Country'] not in Country:
        Country[obj['Country']] = len(Country)+1
    if obj['Location'] not in Location:
        country_id = "NULL" if "Country" not in obj else  Country[obj['Country']]
        Location[obj['Location']] = (len(Location) + 1, country_id)

# User
User = {}
def UserTable(item): 
    processSingleUser(item['Seller'])
    if item['Bids'] is None:
        return
    for bid in item['Bids']: 
        processSingleUser(bid['Bid']['Bidder'])

def processSingleUser(user):
    if user['UserID'] not in User: 
        element = user['Rating']
        if "Location" not in user: 
            element += "|NULL"
        else:
            element += "|" + str(Location[user['Location']][0])
        User[user['UserID']] = element

# Item
Item = {}
def ItemTable(item):
    global Item
    if item['ItemID'] not in Item:
        value = item['Name'] + "|"
        value += transformDollar(item['Currently']) + "|"
        value += transformDollar(item['First_Bid']) + "|"
        value += item['Number_of_Bids'] + "|"
        value += str(Location[item['Location']][0]) + "|"
        value += transformDttm(item['Started']) + "|"
        value += transformDttm(item['Ends']) + "|"
        value +=  item['Description'] if item['Description'] is not None else ""
        Item[item['ItemID']] = value

# Bid
#def BidTable(item):

# ItemCategory
#def ItemCategoryTable(item):

# ItemSeller
#def ItemSellerTable(item):

# ItemBid
#def ItemBidTable(item):

def output():
    with open("Category.dat","w") as f:
        f.write("".join(str(id)  + "|" + item + "\n" for item, id in Category.iteritems())) 

    with open("Country.dat","w") as f: 
        f.write("".join(str(id)  + "|" + country + "\n" for country, id in Country.iteritems())) 

    with open("Location.dat","w") as f: 
        f.write("".join(str(location_id)  + "|"  + location + "|" + str(country_id) + "\n" for location, (location_id, country_id) in Location.iteritems())) 

    with open("User.dat","w") as f: 
        f.write("".join(str(user_id)  + "|" + info + "\n" for user_id, info in User.iteritems()))

    with open("Item.dat","w") as f: 
        f.write("".join(str(item_id)  + "|" + info + "\n" for item_id, info in Item.iteritems())) 


"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print "Success parsing " + f
    
    output()

if __name__ == '__main__':
    main(sys.argv)
