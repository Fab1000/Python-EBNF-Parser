from tkinter import filedialog
from random import choice
from string import ascii_lowercase


class EBNF:
    def __init__(self, start, ebnf, terminals):
        self.start = start
        self.grammar = ebnf
        self.terminals = terminals


# gets path and returns text from file as list of strings
def import_ebnf(filename=None):
    if not filename:
        file = filedialog.askopenfilename(title="Open EBNF File ...", filetype=(("EBNF-Datei", "*.ebnf"), ("Textdatei", "*.txt"), ("Alle Dateiendungen", "*")))

    else:
        file = filename

    filetype = file.split(".")[1]
    
    if filetype != "txt" and filetype != "ebnf":
        print("Only filetype .txt and .ebnf  are allowed!")
        return False        #return 

    with open(file, "r") as ebnf_file:
        return ebnf_file.readlines()


# gets line by line EBNF definition as a list of strings and returns EBNF class object
def read_ebnf(raw_ebnf_grammar):
    ebnf = {}
    
    # delete empty lines
    for line in raw_ebnf_grammar:
        if line == "" or line == "\n":
            raw_ebnf_grammar.remove(line)
    
    # create own non-terminals for internal groups and collect all terminals
    raw_ebnf_grammar, terminalList = outsourceGroupsAndFetchNonTerminalList(raw_ebnf_grammar)

    # spaces will lead to the parser splitting terminals in multiple components
    if " " in terminalList:
        print("Terminals with spaces are not supported in this EBNF parser!")
        return 0

    start = raw_ebnf_grammar[0].split(" ")[0]

    for definition in raw_ebnf_grammar:
        definition = definition.replace("\n", "")
        def_split = definition.split(" ")
        ebnf[def_split[0]] = [def_split[2:]]

        # \n filtern
        for option in ebnf[def_split[0]]:
            for component in option:
                
                # build set of all possible terminals
                if isTerminal(component):
                    terminalList.add(component[1:-1])   # remove " or ' for comparsion with stringToCheck


                # handle |
                if component == "|":
                    ebnf[def_split[0]] = " ".join(def_split[2:]).split("|")

                    for i in range(len(ebnf[def_split[0]])):
                        ebnf[def_split[0]][i] = ebnf[def_split[0]][i].split(" ")

                        for j in ebnf[def_split[0]][i]:
                            if j == "":
                                ebnf[def_split[0]][i].remove(j)
                    
    return EBNF(start, ebnf, terminalList)


# checks if single string is within the given ebnf grammar
def check_string(stringToCheck, ebnf_object):
    stringToCheckLength = len(stringToCheck)    # store value to minimize len() calls
    ebnf = ebnf_object.grammar
    terminalList = ebnf_object.terminals
    option_queue = ebnf[ebnf_object.start][:]    # stores all possible phrases that need to be checked

    # instantly filter out strings with wrong terminals
    copyString = stringToCheck
    for terminal in terminalList:
        copyString = copyString.replace(terminal, "")
    
    if copyString != "":
        return False


    # decide which function should be used to determine which option phrases should be sorted out
    if "" in terminalList or '' in terminalList:
        # non-terminals could potential be resolved to the empty string
        getMinLength = getLengthOfAllTerminals

    else:
        # non-terminals have to be resolved to a string with length > 0
        getMinLength = getMinResultLength   # gets the minimum length the phrase will have


    while option_queue != []:
        current = option_queue.pop(0)[:]   	# get next option from queue, deep copy because references in isOnlyTerminals could change ebnf

        # check if current is a terminal string and matches the input string
        if isOnlyTerminals(current):         # phrase with just terminals
            if "".join(applyTerminals(current)) == stringToCheck:
                return True
            else:
                continue
        
        # every current phrase is checked on fitting leading terminals and fitting terminallength
        # check if leading terminals fit stringToCheck, if not skip current phrase
        if not stringToCheck.startswith(collectLeadingTerminals(current)) or getMinLength(current) > stringToCheckLength:
            continue
        
        for index, component in enumerate(current):     # iterate through all the parts of the current phrase list
            
            # handles terminals
            if isTerminal(component):
                # current component is terminals
                if index == (len(current) - 1) and not stringToCheck.endswith(component[1:-1]):    # String has to end with component
                    break
                elif not component[1:-1] in stringToCheck:      # stingToCheck has to contain terminal
                    break
            

            # current component is non-terminal

            # handles Options []
            elif component.startswith("[") and component.endswith("]"):
                # add with the option
                option_queue += list_replace(current, component, [component[1:-1]])
                current.remove(component)
                # add without the option
                option_queue += [current]
                break


            # Handles Loops {}
            elif component.startswith("{") and component.endswith("}"):
                option_queue += list_replace(current, component, [component[1:-1], component])
                current.remove(component)
                option_queue += [current]
                break


            # Handles non-terminals
            else:
                if component in ebnf:
                        
                    # add all possible definitions for non terminal to option_queue 
                    # because "or" is saved as multiple list items in the ebnf dictionary
                    # for example {"binary_digit": [['"0"'], ['"1"']]}
                    # so binary_digit can be 0 or 1
                    # non-terminals with no option are handled as one option
                    # for example: {"one": [["1"]]}
                    for index in range(len(ebnf[component])):
                        option_queue += list_replace(current, component, ebnf[component][index])
                    
                    break   # continue with next item in option_queue

                else:
                    print("Given EBNF has no Definition for", component)
                    return 0

    return False


# returns length of all terminals + the minimum count of extra terminals the phrase will produce
# the function counts every terminal as length 1
def getMinResultLength(phraseList):
    minimumLength = 0
    for component in phraseList:
        if isTerminal(component):
            # get length of terminal
            minimumLength += len(component[1:-1])

        elif not component.startswith("[") and not component.startswith("{"):
            # count terminal as length 1
            minimumLength += 1

    return minimumLength     


# returns the length of all terminals from given phraseList combined
def getLengthOfAllTerminals(phraseList):
    totalLength = 0
    for component in phraseList:
        if isTerminal(component):
            totalLength += len(component[1:-1])
    
    return totalLength


#collects all leading Terminals of a given phraseList and returns them as one string
def collectLeadingTerminals(phraseList):
    leadingTerminals = ""
    for component in phraseList:
        if isTerminal(component):
            leadingTerminals += component[1:-1]

        else: break

    return leadingTerminals


# checks if given string is marked as Terminal (" or ')
def isTerminal(component):
    return (component.startswith('"') and component.endswith('"')) or (component.startswith("'") and component.endswith("'"))


# removes all the terminal markers " and '
def applyTerminals(phraseList):
    for i, component in enumerate(phraseList):
        if isTerminal(component):
            phraseList[i] = component[1:-1]
    
    return phraseList


# returns True if all items of a list start and end with " or '
def isOnlyTerminals(phraseList):
    for component in phraseList:
        if isTerminal(component):
            continue
        else:
            return False
        
    return True


# collects all groups, creates seperate new terminal definitions for them and builds list of all non-terminals
def outsourceGroupsAndFetchNonTerminalList(raw_ebnf_data):
    # create list of all non-terminals
    nonTerminalList = []
    for line in raw_ebnf_data:
        nonTerminalList += [line.split(" ")[0]]

    terminalList = set()    # set which holds all terminals

    # in case one defintion looks like this: Def = ("a" | "b") ("c" | "d") "f"
    # inside the first iteration the first group will be outsourced: Def = abcde ("c" | "d") "f"
    # then the flag is set to true and the next iteration through all definitions will outsource the second group
    # at the end we have a grammar like this: Def = abcde fghij "f"
    checkAgain = True       # if true the lines will be checked again for grouping

    while checkAgain:
        checkAgain = False

        for definitionIndex, line in enumerate(raw_ebnf_data):
            # Flags
            isDefinition = False    # True if = was read
            isTerminal = False      # Toggles when " or ' was read
            terminalSign = ""       # marker for terminal
            groupFound = False      # True if line has grouping
            
            groupBegin = 0          # index of begin of group
            groupEnd = 0            # index of end of group
            terminalBegin = 0       # index of begin of terminal 
            
            # check for and find group
            for inlineIndex, char in enumerate(line):
                # = was read and we are inside of a definition
                if isDefinition:

                    # charpointer is inside of a terminal
                    if isTerminal:
                        
                        # terminal ends
                        if char == terminalSign:
                            isTerminal = False
                            terminalList.add(line[terminalBegin+1 : inlineIndex])      # slice terminal from line and add it to terminalList
                            
                        continue
                    
                    # charpointer is outside of a terminal
                    elif not isTerminal:
                        
                        # terminal with " begins
                        if char == '"':
                            isTerminal = True
                            terminalSign = '"'
                            terminalBegin = inlineIndex

                        # terminal with ' begins
                        elif char == "'":
                            isTerminal = True
                            terminalSign = "'"
                            terminalBegin = inlineIndex

                        # group begins
                        elif char == "(":
                            # this means that one definiton has more than one group, which need to be handled in the next iteration
                            if groupFound:
                                checkAgain = True
                                break
                            
                            else:
                                groupFound = True
                                groupBegin += inlineIndex
                        
                        # group ends
                        elif char == ")":
                            groupEnd += inlineIndex + 1

                # definition begins
                elif char == "=":
                    isDefinition = True

            
            # extract group and create own definition
            if groupFound:
                    
                    # slice group from line
                    groupString = line[groupBegin:groupEnd]
                    
                    # generate new non terminal name
                    newNonTerminalName = "".join(choice(ascii_lowercase) for i in range(5))
                    while newNonTerminalName in nonTerminalList:
                        newNonTerminalName = "".join(choice(ascii_lowercase) for i in range(5))
                    
                    nonTerminalList += [newNonTerminalName]       # add new name to nonTerminalList 

                    # replace group with new definition
                    raw_ebnf_data[definitionIndex] = line[:groupBegin] + newNonTerminalName + line[groupEnd:]

                    # build new non terminal definition
                    newDefinition = newNonTerminalName + " = " + groupString[1:-1]  # slice of ( and ) from group
                    
                    raw_ebnf_data += [newDefinition]    # add new defnition

    return raw_ebnf_data, terminalList


# replace one item of a list with all the items from another list
def list_replace(list, toReplace, replacementList):
    if toReplace not in list:
        print(f"Element {toReplace} doesnt exist in list {list}")
        return 0

    else:
        isReplaced = False      # flag incase the same non terminal occurs twice in list
        resultList = []         # because only one should be replaced (in this case always the first one)
        for original in list:
            if original == toReplace and not isReplaced:
                for item in replacementList:
                    resultList += [item]
                isReplaced = True       # flag is set, now all instances of toReplace are ignored

            else:
                resultList += [original]
    
    return [resultList]

