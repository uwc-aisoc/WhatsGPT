# ---------------------------------------------------- #
# Dependents: all Datasets/format/ programs            #
# Dependencies: none                                   #
# ---------------------------------------------------- #


def yesNo(prompt):
    response = ""
    yes = ['y', 'Y']
    no = ['n', 'N']
    while response not in yes and response not in no:
        response = input(str(prompt) + " (y/n): ")
        if response in yes:
            return True
        elif response in no:
            return False
        else:
            print(f"Response \'{response}\' not valid, try again: ")

