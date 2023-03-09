# Python-EBNF-Parser
A Python Script which is able to import Extended Backus-Naur Forms from text files and check if a given string is matching the EBNF Rules.

The current Version supports EBNFs which follow the following pattern:

```
Value = ["-"] Number
Number = Digit {Digit}
Digit = "0" | "1" 
```

A definition must be in one line and is not closed with ";". 
Grouping with "()" is also supported. 

The current version doesnt support terminals which have spaces in them like this:
```
Space = " "
``` 

## Usage
Import an EBNF from `.ebnf` or `.txt` with the function `import_ebnf(path)`. This will return the text as a list of strings.
This raw data can than be passed to `read_ebnf(raw_data)` which will return an `EBNF object`.

To check if a certain string is within the rules of an EBNF use the function `EBNF_Object.check_string(string)`.
This will return `True` if the string passed the test and `False` if not.

To generate a list of all possible Strings within an EBNF use `EBNF_Obejct.generateStringList(maxRepetitions)`.
This will return a list of all possible strings. MaxRepetitions must be >= 0 and will control how often Repetitions like `"{SOMETHING}"` will be included in the list. 

## Example
```
import myebnf


PATH = "..."
raw_data = myebnf.importEbnf(PATH)

ebnf = myebnf.readEbnf(raw_data)

print(ebnf.checkString("Hello World!"))
```
