import json
from pathlib import Path, PureWindowsPath
from difflib import get_close_matches
import operator

def getJSON():
    filename = PureWindowsPath("app\\dataset.json")
    correct_path = Path(filename) # Convert path to the right format for the current operating system

    airports = open(correct_path)
    airports = json.load(airports)
    return(airports)

def searchAirports():

    airports = getJSON()["watches"]

    xxx= []
    for i in airports:
        q = i[0].split(" ")
        for j in q:
            if len(j)>2:
                xxx.append(j)

    print(xxx)
    # if len(s)==3:
    #     for i in airports:
    #         if i["IATA_code"]==s.upper():
    #             return(True, i)
    # for i in airports:
    #     if i["city_name"].upper()==s.upper():
    #         return(True, i)
    # # for i in airports:
    # #     if i["airport_name"].upper()==s.upper():
    # #         return(True, i)
    #
    # for i in airports:
    #     if (i["city_name"].upper()).startswith(s.upper()):
    #         return(True, i)
    # # for i in airports:
    # #     if (i["airport_name"].upper()).startswith(s.upper()):
    # #         return(True, i)
    #
    #
    # for i in airports:
    #     if operator.contains(i["city_name"].upper(), s.upper()):
    #         return(True, i)
    # # for i in airports:
    # #     if operator.contains(i["airport_name"].upper(), s.upper()):
    # #         return(True, i)
    #
    # stns = []
    # for i in airports:
    #     stns.append(i["city_name"])
    # t = get_close_matches(s, stns, 1)
    #
    # if len(t)!=0:
    #     for i in airports:
    #         if i["city_name"]==t[0]:
    #             return(False, i)



    # stns = []
    # for i in airports:
    #     stns.append(i["airport_name"])
    # t = get_close_matches(s, stns, 1)
    #
    # if len(t)!=0:
    #     for i in airports:
    #         if i["airport_name"]==t[0]:
    #             return(False, i)

    return(False, False)

print(searchAirports())

def makeHTML():
    airports = getJSON()["airports"]
    for i in airports:
        print("<option> " + str(i["IATA_code"]) + " - " + str(i["city_name"]) + " </option>")
        # print("<option> " + str(i[1]) + " - " + str(i[2]) + " </option>")
# makeHTML()
