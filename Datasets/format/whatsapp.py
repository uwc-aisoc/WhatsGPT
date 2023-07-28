# remove date, time, and usernames
import sys
import time
import os
import snippets

def numberoflines(filepath):
    file = open(filepath, "r")
    count = 0
    # wait=0.001
    while file.readline() != "":
        count = count + 1
        sys.stdout.write("\r" + "Number of lines in file " + filepath + ": " + str(count))
        # use this format of stdout write with \r for dynamic one line printing
        # time.sleep(wait) #check if dynamic
    file.close()
    print()
    return count


# ----These are pattern deleters----
def remDate(text): # Hyphens
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
        # print("No hyphen found")
        return [text, text, len(text), False]


def remName(text): # Colons
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
        # print("No colon found")
        return [text, text, len(text), False]


# They return an array, [date/name, pruned string, position of hyphen or colon, flag]
# flag is whether or not there was a date or name detected
# if no date or name was detected, [0] and [1] are the original text passed
# the normal range for position for hyphen should be 15-18. colon 17 or 19 for Chris/Katya
# ----------------------------------

def validLine(text, names):
    # returns 0 on normal, 1 on blacklist items. 2 if suspicious
    rD = remDate(text)  # these assignments are to prevent the function from being called more than once
    date = rD[0]
    noDate = rD[1]  # line without the date
    hyphenPos = rD[2]
    hyphenFound = rD[3]
    rN = remName(noDate)
    name = rN[0]
    message = rN[1].replace("\n","") # messages end in a newline. need to del \n to properly work with blacklist
    # print(f"The message is {message}")
    # colonPos = rN[2]
    colonFound = rN[3]
    # todo: make regex blacklist to remove "A removed B" or "A added C" etc.
    blacklist = ["<Media omitted>",
                 "Missed voice call",
                 "Missed video call",
                 "This message was deleted"] # blacklist messages, case sensitive, strict ('==', not 'in')
    # ngl this trace table format is giving me cancer
    if hyphenFound and colonFound:
        if 16 <= hyphenPos <= 19:  # the dates are 15-18 long, but the hyphens are one after that
            for phrase in blacklist:
                # print(phrase+message)
                if phrase == message:
                    # print(f"blocked {phrase}")
                    return 1
            if name in names:
                return 0
            else:
                recognised = snippets.yesNo(f'Name not in names list: {name}. Is this name acceptable?')
                if recognised:
                    print("Added to names list")
                    names.append(name)
                    return 0
                else:
                    return 1
                # maybe add something here to add the name to the list of names
        else:
            acceptable = snippets.yesNo(
                f"The date is of abnormal length {hyphenPos} as opposed to range 16-19. Is \'{date}\' a normal date?")
            if acceptable:
                if name in names:
                    return 0
                else:
                    recognised = snippets.yesNo(f'Name not in names list: {name}. Is this name acceptable?')
                    if recognised:
                        print("Added to names list")
                        names.append(name)
                        return 0
                    else:
                        return 1
            elif not acceptable:
                return 0
            else:
                sys.exit("Boolean exception")
    else:
        return 2 # this part represents lines without a date or name. leave this to be checked by user


# filepathr = "./Datasets/"+input("Name of input file: ")
print("Select file to read from:")
filepathr = snippets.fileexplorer(fileMustExist=True)
fileR = open(filepathr, "rb")
names = []
response = input("Type name(s) of people in the chat, case sensitive. Leave blank to continue: ")
while not response == "":
    names.append(response)
    response = input("Continue. Leave blank to continue: ")

invalidLines = []
invalidPos = []
# in format [start, end] where the invalid line starts and ends on the aforementioned numbers' byte location

# IMPORTANT TO USE BYTE MODE TO AVOID PROBLEMS WITH BYTE ADDRESSES!!!

for i in range(1, numberoflines(filepathr) + 1):
    currentPos=fileR.tell()
    line = fileR.readline().decode('utf-8', 'strict') # decode from bytes
    valid = validLine(line, names) #0,1,2
    if not valid==0:
        sys.stdout.write(f"\rLine {i} invalid. ")
        invalidLines.append([i,valid])
        invalidPos.append([currentPos,fileR.tell(),valid]) # [start of line, end of line]
    #time.sleep(0.001)
print(f"\n{len(invalidPos)} lines found invalid (not connected to a time, or contains media that cannot be processed)")
# Important reminder: Remember to use bytes mode when reading and encode in 'utf-8', 'strict' before passing on to file

# filepathw = "./Datasets/"+str(input("Input file name: "))
print("Select output file:")
filepathw = snippets.fileexplorer()
fileW = open(filepathw, 'wb')
fileW.seek(0)
fileR.seek(0)
person = names[int(input(f"Which person? Type the index number: {names}"))]
name = "Placeholder, as this is likely the first message of the chat"
lineW = "Placeholder, as this is likely the first message of the chat"

#this first section handles non-invalid lines
message: bytes="Placeholder".encode('utf-8')
for stend in invalidPos: # start/end pairs
    # print(f"Current fileR position@1: {fileR.tell()}") # all fileR position@x are for debugging where cursor is
    while fileR.tell() < stend[0]:
        lineW=fileR.readline().decode('utf-8') # this moves the position too. this is already decoded!
        name=remName(remDate(lineW)[1])[0]
        message=remName(remDate(lineW)[1])[1]
        if person == name:
            fileW.write(remName(remDate(lineW)[1])[1].encode('utf-8'))  # read to next invalid position. have to de- and en- code as well to prune to messages only
    # print(f"Current fileR position@2: {fileR.tell()}")
    # this second part handles invalid lines
    # print(f'{stend[0]} to {stend[1]}:')
    text=fileR.read(stend[1]-stend[0])
    # print(f"Current fileR position@3: {fileR.tell()}")
    if name == person and not stend[2] == 1: # first operator actually checks if the LAST LINE WITH A NAME ASSOCIATED is the same as the person being looked for. stend2-->1 means it is definitely not right
        print("The stend code passed is",stend[2])
        if snippets.yesNo('Text independent of message metadata: \'' + text.decode("utf-8", "strict").replace("\n","") + '\'. Keep?\nThe last message was ' + lineW.replace(
                "\n",
                "") + '\''):  # this is really verbose because f strings can't evaluate backslashes for some god forsaken reason
            fileW.write(text)
        else:
            print(f"Skipping {stend[0]}-{stend[1]}")
            # print(f"Current fileR position@4: {fileR.tell()}")
    # else: # debugging
    #     if stend[2]==2: # it is either 2 or 1.
    #         print(f"Blocked name: {name}")
    #     else:
    #         print(f"Blocked phrase: {message} due to code {stend[2]}")

