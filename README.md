
# crush-party-software

### repository overview

this is a simple implementation of the matching software that can be used to prepare for the annual Crush Party event at Rice University

### dependencies

* python3
* latexmk

### instructions

1. update the `format.txt` document
    * the keys define the type of information, and the values define the name of the column in which that information resides (example: `name: B` means that the names of the participants reside in Column B)
    * if multiple columns holds related but different information for a given key, separate those columns with a space (example: `matches1: F G`) and specify the sub-type of each of those columns below (example: `F: Romantic`)
    * if multiple columns holds the exact same type of information, you can concatenate those column names with OR-notation (example: `I|J|K: Major`)
1. update the `questions.txt` document
    * the matrix at the top defines how similar answer choices are to one another
    * the text below define which question and answers the matrix is in reference to
1. move the data into the top-level-folder and name it `data.csv`
1. run the matching software: `python3 match.py`
1. compile the results: `cd results` then `make`
1. print the documents and enjoy the event!
