# ---------------------------------------------------- #
# Dependents: all Datasets/format/ programs            #
# Dependencies: os, yesNo.py                           #
# ---------------------------------------------------- #


import os
import yesNo

def fileexplorer(fileMustExist=False,directoriesSelectable=False):
    print(f"Selected file must exist?: {fileMustExist}")
    print(f"Directories are selectable?: {directoriesSelectable}")
    print("Note: This program cannot create directories.") # todo: allow creation of directories
    while True:
        cwdpath = ""
        print(f"Current directory: {os.getcwd()}\nDirectory contents:\n{os.listdir()}\n.. and . are accepted")
        cwdpath: str = input("Select file or directory: ")
        if os.path.isdir(cwdpath):
            if directoriesSelectable and yesNo("Do you wish to select this directory? If not, this program will change directories instead"):
                return os.getcwd()+"/"+cwdpath+"/"
            print(f">cd {cwdpath}")
            os.chdir(cwdpath)
        elif os.path.isfile(cwdpath):
            if yesNo(f"Confirm: {cwdpath}"):
                return os.getcwd()+"/"+cwdpath
            else:
                print("Cancelled, reenter:")
        elif not fileMustExist:
            if yesNo(f"You are attempting to return a FILE that does not exist. This likely means that the program will create it instead.\nConfirm: {cwdpath}"):
                return os.getcwd()+"/"+cwdpath
            else:
                print("Cancelled, reenter:")
        else:
            print("The path does not exist. Please try again.")