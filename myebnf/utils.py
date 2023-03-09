from random import choice
from string import ascii_lowercase

"""
This file holds all utility functions used inside the EBNF class
"""

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


# splits a string into a list of its components
def splitComponents(raw_definition):
    componentList = []

    # Flags
    isTerminal = False          # is True if the current char is within a terminal
    terminalSign = ""           # holds " or ' depending on the terminal-marking
    isComponent = False         # is True if the current char is within a terminal (so no space or inside terminal)
    componentBegin = 0          # holds the index of the current components beginning

    for inlineIndex, char in enumerate(raw_definition):
        
        if isTerminal:   
            # terminal ends
            if char == terminalSign:
                isTerminal = False

                # incase of for example: "["-"]" isComponent and isTerminal are True at the same point
                if not isComponent:
                    # slice terminal from line and add it as a component
                    componentList += [raw_definition[componentBegin : inlineIndex+1]]     
        
        # charpointer is outside of a terminal
        elif not isTerminal:
            
            # terminal with " begins
            if char == '"':
                isTerminal = True
                terminalSign = '"'

                # incase of for example: "["-"]" isComponent and isTerminal are True at the same point
                if not isComponent:
                    componentBegin = inlineIndex

            # terminal with ' begins
            elif char == "'":
                isTerminal = True
                terminalSign = "'"

                # incase of for example: "["-"]" isComponent and isTerminal are True at the same point
                if not isComponent:
                    componentBegin = inlineIndex

            # component ends
            elif char == " " and isComponent:
                componentList += [raw_definition[componentBegin : inlineIndex]]
                isComponent = False

            # new component begins
            elif char != " " and not isComponent:
                componentBegin = inlineIndex
                isComponent = True
    
    if char != " " and (isComponent or isTerminal):
        componentList += [raw_definition[componentBegin : inlineIndex+1]]

    return componentList
            
