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

To check if a certain string is within the rules of an EBNF use the function `check_string(string, EBNF_Object)`.
This will return `True` if the string passed the test and `False` if not.
