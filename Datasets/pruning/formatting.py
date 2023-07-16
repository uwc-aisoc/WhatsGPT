# remove date, time, and usernames
import sys
import time


def yesNo(prompt):
    response = ""
    validResponses = ['y', 'n', 'Y', 'N']
    yes = ['y', 'Y']
    no = ['n', 'N']
    while not response in validResponses:
        response = input(str(prompt) + " (y/n): ")
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
    flag = False
    for i in range(len(text)):
        # print(text[i], i)
        if text[i] == "-":
            # print("Hyphen found at index", str(i) + ". Halt")
            flag = True
            return [text[:i - 1], text.replace(text[:(i + 2)], ""), i, True]
            # -1 to remove the trailing space
            # +2 because +1 for offset [:x] starts at 1. another +1 for the sapce after hyphen
    if not flag:
        print("No hyphen found")
        return [text, text, len(text), False]


def remName(text):
    # repeat process with ":", always works as long as contact name does not have colon
    # this DOES NOT work to simply prune the entire thing to just the message too, since the time has a colon as well
    flag = False
    for i in range(len(text)):
        # print(text[i], i)
        if text[i] == ":":
            # print("Colon found at index", str(i) + ". Halt")
            flag = True
            return [text[:i], text.replace(text[:(i + 2)], ""), i, True]
            # +2 for same reasons as above. no -1 as there is no trailing space
    if not flag:
        print("No colon found")
        return [text, text, len(text), False]


# They return an array, [date/name, pruned string, position of hyphen or colon, flag]
# flag is whether or not there was a date or name detected
# if no date or name was detected, [0] and [1] are the original text passed
# the normal range for position for hyphen should be 15-18. colon 17 or 19 for Chris/Katya
# ----------------------------------

def validLine(text, names):
    # returns True on normal, False on not line. if suspicious, user will be prompted
    rD = remDate(text)  # these assignments are to prevent the function from being called more than once
    date = rD[0]
    noDate = rD[1]  # line without the date
    hyphenPos = rD[2]
    hyphenFound = rD[3]
    rN = remName(noDate)
    name = rN[0]
    # message = rN(noDate)[1]
    # colonPos = rN(noDate)[2]
    colonFound = rN[3]

    if hyphenFound and colonFound:
        if hyphenPos >= 16 and hyphenPos <= 19:  # the messages are 15-18 long, but the hyphens are one after that
            if "<Media omitted>" in text:
                print("Media omitted found")
                return False
            if name in names:
                return True
            else:
                return yesNo(f'Name not in names list: {name}. Is this name acceptable?')
                # maybe add something here to add the name to the list of names
        else:
            acceptable = yesNo(
                f"The date is of abnormal length {hyphenPos} as opposed to range 16-19. Is \'{date}\' a normal date?")
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


names = []
response = input("Type name(s) of people in the chat, case sensitive. Leave blank to continue: ")
while not response == "":
    names.append(response)
    response = input("Continue. Leave blank to continue: ")

invalidLines = []
invalidPos = []
# in format [start, end] where the invalid line starts and ends on the aforementioned numbers' byte location
filepathr = "./Datasets/Katya Swaminathan Censored.txt"
fileR = open(filepathr, "rb")
# IMPORTANT TO USE BYTE MODE TO AVOID PROBLEMS WITH BYTE ADDRESSES!!!
for i in range(1, numberoflines(filepathr) + 1):
    currentPos=fileR.tell()
    line = fileR.readline().decode('utf-8', 'strict') # decode from bytes
    valid = validLine(line, names)
    if not valid:
        print(f"Line {i} invalid\n")
        invalidLines.append(i)
        invalidPos.append([currentPos,fileR.tell()])
    #time.sleep(0.01)

# Important reminder: Remember to use bytes mode when reading and encode in 'utf-8', 'strict' before passing on to file

filepathw = "./Datasets/"+str(input("input file name"))
fileW = open(filepathw, 'wb')
fileW.seek(0)
fileR.seek(0)
person = names[int(input(f"Which person? Type the index number: {names}"))]
name = "Placeholder, as this is likely the first message of the chat"
for stend in invalidPos: # start/end pairs
    print(f"Current fileR position@1: {fileR.tell()}")

    while fileR.tell() < stend[0]:
        lineW=fileR.readline().decode('utf-8') # this moves the position too.
        name=remName(remDate(lineW)[1])[0]
        if person == name:
            message=remName(remDate(lineW)[1])[1]
            fileW.write(message.encode('utf-8'))  # read to next invalid position. have to de- and en- code as well to prune to messages only
            print(f'Sent \'{message}\'')
        else:
            print(f"skipped, as name was \'{name}\', not \'{person}\'")

    print(f"Current fileR position@2: {fileR.tell()}")
    print(f'{stend[0]} to {stend[1]}:')
    text=fileR.read(stend[1]-stend[0])
    print(f"Current fileR position@3: {fileR.tell()}")
    if "<Media omitted>" not in text.decode('utf-8','strict'):
        if name == person:
            if yesNo(f'Text independent of message metadata: {text.decode("utf-8", "strict")}. Keep?\nThe last message was \'{line}\''):
                fileW.write(text)
            else:
                print(f"Skipping {stend[0]}-{stend[1]}")
                print(f"Current fileR position@4: {fileR.tell()}")
        else:
            print(f"Skipped: name was \'{name}\' instead of \'{person}\'")
    else:
        print("<Media omitted> skip")
