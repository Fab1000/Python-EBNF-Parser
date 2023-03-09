from tkinter import filedialog

from . import utils

# uncommend if you want to execute this file as __main__
#import utils

class EBNF:
    def __init__(self, start, ebnf, terminals):
        self.start = start
        self.grammar = ebnf
        self.terminals = terminals

    
    # checks if single string is within the given ebnf grammar
    def checkString(self, stringToCheck):
        stringToCheckLength = len(stringToCheck)    # store value to minimize len() calls
        ebnf = self.grammar
        terminalList = self.terminals
        option_queue = ebnf[self.start][:]    # stores all possible phrases that need to be checked

        # instantly filter out strings with wrong terminals
        copyString = stringToCheck
        for terminal in terminalList:
            copyString = copyString.replace(terminal, "")
        
        if copyString != "":
            return False


        # decide which function should be used to determine which option phrases should be sorted out
        if "" in terminalList or '' in terminalList:
            # non-terminals could potential be resolved to the empty string
            getMinLength = utils.getLengthOfAllTerminals

        else:
            # non-terminals have to be resolved to a string with length > 0
            getMinLength = utils.getMinResultLength   # gets the minimum length the phrase will have


        while option_queue != []:
            current = option_queue.pop(0)[:]   	# get next option from queue, deep copy because references in isOnlyTerminals could change ebnf

            # check if current is a terminal string and matches the input string
            if utils.isOnlyTerminals(current):         # phrase with just terminals
                if "".join(utils.applyTerminals(current)) == stringToCheck:
                    return True
                else:
                    continue
            
            # every current phrase is checked on fitting leading terminals and fitting terminallength
            # check if leading terminals fit stringToCheck, if not skip current phrase
            if not stringToCheck.startswith(utils.collectLeadingTerminals(current)) or getMinLength(current) > stringToCheckLength:
                continue
            
            for index, component in enumerate(current):     # iterate through all the parts of the current phrase list
                
                # handles terminals
                if utils.isTerminal(component):
                    # current component is terminals
                    if index == (len(current) - 1) and not stringToCheck.endswith(component[1:-1]):    # String has to end with component
                        break
                    elif not component[1:-1] in stringToCheck:      # stingToCheck has to contain terminal
                        break
                

                # current component is non-terminal

                # handles Options []
                elif component.startswith("[") and component.endswith("]"):
                    # add with the option
                    option_queue += utils.list_replace(current, component, [component[1:-1]])
                    current.remove(component)
                    # add without the option
                    option_queue += [current]
                    break


                # Handles Loops {}
                elif component.startswith("{") and component.endswith("}"):
                    option_queue += utils.list_replace(current, component, [component[1:-1], component])
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
                            option_queue += utils.list_replace(current, component, ebnf[component][index])
                        
                        break   # continue with next item in option_queue

                    else:
                        print("Given EBNF has no Definition for", component)
                        return 0

        return False


    # returns list with all possible strings inside the rules and iteration limitiations
    def generateStringList(self, maxRepetitions=1):
        # assert maxRepetitions >= 0
        if maxRepetitions < 0: maxRepetitions = 0
        
        stringList = set()                      # holds all possible strings at the end

        ebnf = self.grammar
        option_queue = ebnf[self.start][:]      # stores all possible phrases that need to be resolved

        while option_queue != []:
            current = option_queue.pop(0)[:]   	# get next option from queue, deep copy because references in isOnlyTerminals could change ebnf

            # check if current is a terminal string and matches the input string
            if utils.isOnlyTerminals(current):                          # phrase with just terminals
                stringList.add("".join(utils.applyTerminals(current)))  # add current to stringList
                continue
            
            
            for index, component in enumerate(current):     # iterate through all the parts of the current phrase list
                
                # handles terminals
                if utils.isTerminal(component):
                    continue

                # current component is non-terminal

                # handles Options []
                elif component.startswith("[") and component.endswith("]"):
                    # add with the option
                    option_queue += utils.list_replace(current, component, [component[1:-1]])
                    current.remove(component)
                    # add without the option
                    option_queue += [current]
                    break


                # Handles Repetitions {}
                elif component.startswith("{") and component.endswith("}"):
                    # split the repetition into all options smaller or equal to maxRepetitions
                    for i in range(maxRepetitions+1):
                        # add current with i*component
                        option_queue += utils.list_replace(current, component, [component[1:-1]]*i)
                    
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
                            option_queue += utils.list_replace(current, component, ebnf[component][index])
                        
                        break   # continue with next item in option_queue

                    else:
                        print("Given EBNF has no Definition for", component)
                        return False

        return stringList
        

# Setup Functions

# gets path and returns text from file as list of strings
def importEbnf(filename=None):
    if not filename:
        file = filedialog.askopenfilename(title="Open EBNF File ...", filetype=(("EBNF-File", "*.ebnf"), ("Textfile", "*.txt"), ("All files", "*")))

    else:
        file = filename

    filetype = file.split(".")[1]
    
    if filetype != "txt" and filetype != "ebnf":
        print("Only filetype .txt and .ebnf  are allowed!")
        return False        #return 

    with open(file, "r") as ebnf_file:
        return ebnf_file.readlines()


# gets line by line EBNF definition as a list of strings and returns EBNF class object
def readEbnf(raw_ebnf_grammar):
    ebnf = {}
    
    # delete empty lines
    for line in raw_ebnf_grammar:
        if line == "" or line == "\n":
            raw_ebnf_grammar.remove(line)
    
    # create own non-terminals for internal groups and collect all terminals
    raw_ebnf_grammar, terminalList = utils.outsourceGroupsAndFetchNonTerminalList(raw_ebnf_grammar)

    # create necessary data structs for EBNF object: start: string, grammar: dict, terminalList: list        
    start = raw_ebnf_grammar[0].split(" ")[0]

    for definition in raw_ebnf_grammar:
        definition = definition.replace("\n", "")
        def_split = utils.splitComponents(definition)
        ebnf[def_split[0]] = [def_split[2:]]

        # \n filtern
        for option in ebnf[def_split[0]]:
            for component in option:
                
                # build set of all possible terminals
                if utils.isTerminal(component):
                    terminalList.add(component[1:-1])   # remove " or ' for comparsion with stringToCheck


                # handle |
                if component == "|":
                    # join the defintion back together and split them in options (" | ")
                    ebnf[def_split[0]] = " ".join(def_split[2:]).split(" | ")   # automatically removes spaces " | "

                    for i in range(len(ebnf[def_split[0]])):
                        # split every option into their components
                        ebnf[def_split[0]][i] = utils.splitComponents(ebnf[def_split[0]][i])

                    break
                    
    return EBNF(start, ebnf, terminalList)
