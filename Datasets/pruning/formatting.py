# remove date, time, and usernames
import sys
import time


def yesNo(prompt):
    response = ""
    validResponses = ['y', 'n', 'Y', 'N']
    yes = ['y','Y']
    no = ['n','N']
    while not response in validResponses:
        response = input(str(prompt)+" (y/n): ")
        if response in yes:
            return True
        elif response in no:
            return False
        else:
            print(f"Response \'{response}\' not valid, try again: ")

def recogniseDate(line):  # so far, this function looks for the narrow no break space

    # dates are in the format M/D/YY, H:MM (AM/PM). both Hour, Month and Day can be either one or two numbers long.
    # Year is the last two digits of the current year
    # At the end of the date/time, there is a hyphen ("-") surrounded by spaces
    # There is also a Narrow No Break Space or NNBSP (" ") between the time and meridian marker (AM/PM)
    # e.g: "6/9/22, 2:13 PM - [Name]: Just in case :)"
    return " " in line

def numberoflines(filepath):
    file = open(filepath, "r")
    count = 0
    # wait=0.001
    while (file.readline() != ""):
        count = count + 1
        sys.stdout.write("\r" + "Number of lines in file " + filepath + ": " + str(count))
        # use this format of stdout write with \r for dynamic one line printing
        # time.sleep(wait) #check if dynamic
    file.close()
    return count


# ----These are pattern deleters----
def remDate(text):
    flag=False
    for i in range(len(text)):
        # print(text[i], i)
        if text[i] == "-":
            # print("Hyphen found at index", str(i) + ". Halt")
            return [text[:i], text.replace(text[:(i + 2)], ""), i,  True]
            # +2 because +1 for offset [:x] starts at 1. another +1 for the sapce after hyphen
    if not flag:
        print("No hyphen found")
        return [text, text, i, False]


def remName(text):
    # repeat process with ":", always works as long as contact name does not have colon
    flag = False
    for i in range(len(text)):
        # print(text[i], i)
        if text[i] == ":":
            # print("Colon found at index", str(i) + ". Halt")
            return [text[:i], text.replace(text[:(i + 2)], ""), i, True]
            # +2 for same reasons as above
    if not flag:
        print("No colon found")
        return [text, text, i, False]


# They return an array, [date/name, pruned string, position of hyphen or colon, flag]
# flag is whether or not there was a date or name detected
# if no date or name was detected, [0] and [1] are the original text passed
# the normal range for position for hyphen should be 15-18. colon 17 or 19 for Chris/Katya
# ----------------------------------

def validLine(text, names):
    # returns True on normal, False on not line. if suspicious, user will be prompted
    date = remDate(text)[0]
    noDate = remDate(text)[1] # line without the date
    hyphenPos = remDate(text)[2]
    hyphenFound = remDate(text)[3]
    name = remName(noDate)[0]
    # message = remName(noDate)[1]
    # colonPos = remName(noDate)[2]
    colonFound = remName(noDate)[3]

    if hyphenFound and colonFound:
        if hyphenPos < 15 or hyphenPos > 18:
            if name in names:
                return True
            else:
                return yesNo(f'Name not in names list: {name}. Is this name acceptable?')
                # maybe add something here to add the name to the list of names
        else:
            acceptable = yesNo(f"The date is of abnormal length. Is \'{date}\' a normal date?")
            if acceptable:
                if name in names:
                    return True
                else:
                    return yesNo(f'Name not in names list: {name}. Is this name acceptable?')
                    # maybe add something here to add the name to the list of names
            elif not acceptable:
                return False
            else:
                sys.exit("Boolean exception")
    else:
        return False


filepath = "../Katya Swaminathan Censored.txt"
file = open(filepath, "r")
# print("\n"+ str(numberoflines(filepath)))

for i in range(numberoflines(filepath)):
    print(f'Line {i+1} is valid: {validLine(file.readline())}')

# dehyp = remDate(input("Enter message with hyphen"))
# print("Deyphenated:", dehyp[1])
# print("Decolonated:", remName(dehyp[1])[1])
