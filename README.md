
# crush-party-software

### repository overview

this is an implementation of the matching software used for the annual Crush Party event at Rice University

### dependencies

* python3
* latexmk

### instructions

1. update the `format.txt` document (several examples available)
    * the keys define the type of information, and the values define the name of the column in which that information resides (example: `name: B` means that the names of the participants reside in Column B)
    * if multiple columns holds related but different information for a given key, separate those columns with a space (example: `matches1: F G`) and specify the sub-type of each of those columns below (example: `F: Romantic`)
    * if multiple columns holds the exact same type of information, you can concatenate those column names with OR-notation (example: `I|J|K: Major`)
1. update the `questions.txt` document (several examples available)
    * the matrix at the top defines how similar answer choices are to one another
    * the text below define which question and answers the matrix is in reference to
    * the SPACING of this file is very important
        * there should be ZERO newlines at the top of the file
        * there should be TWO newlines at the bottom of the file
        * there should be ONE newline between each section of the file
    * the CONTENTS of this file is very important; make sure the text in this file EXACTLY matches the text in the `data.csv` file (whether `...` is typed as one character or three, whether `'` is typed as a straight vertical quote or a curved "smart" quote, typos and spelling mistakes, etc)
1. move the data into the top-level-folder and name it `data.csv`
1. run the matching software: `python3 match.py`
1. compile the results: `cd results` then `make`
1. print the documents and enjoy the event!
