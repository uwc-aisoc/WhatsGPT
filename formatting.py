import sys
import time
def recogniseDate(line): #so far, this function looks for the narrow no break space

    # dates are in the format M/D/YY, H:MM (AM/PM). both Hour, Month and Day can be either one or two numbers long.
    # Year is the last two digits of the current year
    # At the end of the date/time, there is a hyphen ("-") surrounded by spaces
    # There is also a Narrow No Break Space or NNBSP (" ") between the time and meridian marker (AM/PM)
    # e.g: "6/9/22, 2:13 PM - Christopher Ginting: Just in case :)"
    return " " in line

def recogniseLine(line): #so far, this function looks for the newlines
    return "\n" in line

def numberoflines(filepath):
    file=open(filepath, "r")
    count=0
    #wait=0.001
    while(file.readline() != ""):
        count = count+1
        sys.stdout.write("\r" + "Number of lines in file "+filepath+": " + str(count))
        #use this format of stdout write with \r for dynamic one line printing
        #time.sleep(wait) #check if dynamic
    return count

def returnMessage(text):
    print() #newline
    message=False
    for char in text:
        if char == "-":
            message = True


filepath="./Datasets/Katya Swaminathan Censored.txt"
print("\n"+ str(numberoflines(filepath)))



