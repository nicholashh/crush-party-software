
import sys, csv



### STEP 1: Parse the format file. ###

print("Step 1", flush=True)

index_of_ = {}
meaning_of_ = {}

with open('format.txt', 'r') as format_file:

    for row in format_file:
        row = row.strip()

        if row == "": continue

        format_entry = row.split(":")
        key = format_entry[0]
        value = format_entry[1]

        def char_to_index (char_array):
            # create the array of indices to output
            index_array = []
            # for each column in the format key
            for column in char_array:
                # if this entry references multiple columns
                if "|" in column:
                    # parse each of the column letters individually
                    index_array.append(char_to_index(column.split("|")))
                else:
                    # convert that column to integers (where A->1, etc)
                    output_item = []
                    for char in column:
                        output_item.append(ord(char.upper())-64)
                    # account for columns after Z (like AA->27, etc)
                    index_item = 0
                    length = len(output_item)
                    for index, element in enumerate(output_item):
                        index_item += pow(26, length - index - 1) * element
                    # offset each index by 1 (A->0, AA->26)
                    index_array.append(index_item - 1)
            # return the array of indices
            return index_array

        valid_keys_one = ["name", "email", "gender"]
        valid_keys_multiple = ["matches1", "matches2", "info", "questions"]
        valid_keys = valid_keys_one + valid_keys_multiple

        if key in valid_keys:

            key = key
            value = value.split(" ")[1:]

            index_of_[key] = char_to_index(value)

            if key in valid_keys_one:
                index_of_[key] = index_of_[key][0]

        else:

            key = key.split("|")
            value = value.strip()

            meaning_of_[tuple(char_to_index(key))] = value

index_of_overall = tuple([-1])
meaning_of_[index_of_overall] = "Overall"

def newtuple (index):
    if type(index) is list:
        index = tuple(index)
    elif type(index) is int:
        index = tuple([index])
    return index

new_matches2_index = []
for index in index_of_["matches2"]:
    index = newtuple(index)
    new_matches2_index.append(index)
index_of_["matches2"] = new_matches2_index



### STEP 2: Parse the data file. ###

print("Step 2", flush=True)

people = {}

string2constant = {}
constant2string = {}
constant = 0

column_headers = {}

def getNetID (person):

    return constant2string[person[index_of_["email"]]].split("@")[0].lower()

with open('data.csv', 'r', encoding='utf-8') as data_file:

    i = 0
    for row in csv.reader(data_file):
        i += 1

        if i == 1:
            expected_num_answers = len(row)

        person = []
        for term in row:
            if term not in string2constant:
                string2constant[term] = constant
                constant2string[constant] = term
                constant += 1
            person.append(string2constant[term])

        if len(person) != expected_num_answers:
            print("a row in data.csv is invalidly formatted")
            continue

        person = tuple(person)
        if i == 1:
            column_headers = person
        else:
            people[getNetID(person)] = person



### STEP 3 [OPTIONAL]: Parse the questions file. ###

print("Step 3", flush=True)

questions_are_weighted = True

weight = {}

try:

    with open('questions.txt', 'r', encoding='utf-8') as questions_file:

        weights = []

        parsing_weights = True
                
        question_id = 0
        answers = []
        new_question = True

        for row in questions_file:
            row = row.strip()

            if row == "":

                if parsing_weights:

                    parsing_weights = False
                    continue

                else:

                    question_weights = weights[len(weight)]

                    if len(answers) == len(question_weights) \
                            and question_id != -1:

                        new_entry = {}
                        for index in range(len(answers)):
                            new_entry[answers[index]] = question_weights[index]

                        weight[column_headers.index(question_id)] = new_entry

                    else:

                        print("questions.txt file is invalidly formatted")
                        questions_are_weighted = False
                        break
                
                question_id = 0
                answers = []
                new_question = True
                continue

            if parsing_weights:

                question = []
                for num in row.split(" "):
                    question.append(float(num))
                weights.append(question)

            else:

                if row in string2constant:

                    string_id = string2constant[row]

                else:

                    print("no one chose answer: " + 
                            str(row.encode('ascii', 'replace')), flush=True)
                    string_id = -1

                if new_question:
                    question_id = string_id
                    new_question = False
                else:
                    answers.append(string_id)

except IOError:

    print("questions.txt file does not exist", flush=True)
    questions_are_weighted = False



### STEP 4: Compute similarity scores. ###

print("Step 4", flush=True)

similarity_scores = {}

for person1id in people:
    for person2id in people:
        if person1id != person2id:

            person1 = people[person1id]
            person2 = people[person2id]
            score = 0.0

            for question in index_of_["questions"]:

                person1answer = person1[question]
                person2answer = person2[question]

                if questions_are_weighted:

                    question_weight = weight[question]
                    person1weight = 1.0 * question_weight[person1answer]
                    person2weight = 1.0 * question_weight[person2answer]

                    score += 1.0 - abs(person1weight - person2weight)

                elif person1answer == person2answer:

                    score += 1

            names1 = (getNetID(person1), getNetID(person2))
            names2 = (names1[1], names1[0])
            similarity_scores[names1] = score
            similarity_scores[names2] = score



### STEP 5: Compute compatible matches. ###

print("Step 5", flush=True)

matches = {}
emptyID = string2constant[""]

for person1id in people:
    person1 = people[person1id]
    new_matches_results = {}
    for index1 in index_of_["matches1"]:

        new_matches_list = []
        for pair in similarity_scores:
            if pair[0] == person1id:
                person2id = pair[1]
                person2 = people[person2id]
                score = similarity_scores[pair]
                
                person1gender = constant2string[person1[index_of_["gender"]]]
                person2gender = constant2string[person2[index_of_["gender"]]]

                the_gender_binary = ["Male", "Female"]
                practically_perfect_in_every_way = "Other"
                if person1gender not in the_gender_binary:
                    person1gender = practically_perfect_in_every_way
                if person2gender not in the_gender_binary:
                    person2gender = practically_perfect_in_every_way

                person1options = constant2string[person1[index1]]
                person2options = constant2string[person2[index1]]

                if person2gender in person1options:
                    if person1gender in person2options:
                        new_matches_list.append((person2id, score))

        new_matches_results[index1] = {}
        new_matches_results[index1][index_of_overall] = new_matches_list

        all_matches = new_matches_list
        for index2 in index_of_["matches2"]:
            new_matches_list = []
            for pair in all_matches:
                person2id = pair[0]
                person2 = people[person2id]

                persion1values = []
                persion2values = []
                for index3 in index2:
                    persion1values.append(person1[index3])
                    persion2values.append(person2[index3])

                compatible = False
                for value1 in persion1values:
                    if value1 != emptyID:
                        for value2 in persion2values:
                            if value2 != emptyID:
                                if value1 == value2:
                                    compatible = True

                if compatible:
                    new_matches_list.append(pair)

            new_matches_results[index1][index2] = new_matches_list

    matches[person1id] = new_matches_results



### STEP 6: Compute best matches. ###

print("Step 6", flush=True)

index_of_["matches2"] = [index_of_overall] + index_of_["matches2"]

for person1id in matches:
    for index1 in index_of_["matches1"]:
        for index2 in index_of_["matches2"]:
            matches[person1id][index1][index2] = sorted(
                    matches[person1id][index1][index2],
                    key = lambda pair: -pair[1])[:10]



### STEP 7: Output best matches. ###

print("Step 7", flush=True)

num_questions = len(index_of_["questions"])

for person1id in people:
    person1 = people[person1id]

    netID = getNetID(person1)
    fileName = './results/' + netID + '.tex'
    with open(fileName, 'w', encoding='utf-8') as output_file:

        output_file.write("\n")
        output_file.write("\\documentclass[a4paper]{article}\n")
        output_file.write("\n")
        output_file.write("\\usepackage[english]{babel}\n")
        output_file.write("\\usepackage[utf8]{inputenc}\n")
        output_file.write("\\usepackage{parskip}\n")
        output_file.write("\n")
        output_file.write("\\usepackage{geometry}\n")
        output_file.write("\\geometry{\n")
        output_file.write("    tmargin   = 1.5 in,\n")
        output_file.write("    lmargin   = 1.00 in,\n")
        output_file.write("    rmargin   = 1.00 in,\n")
        output_file.write("    bmargin   = 1.00 in,\n")
        output_file.write("    headheight  = 0.50 in,\n")
        output_file.write("    headsep   = 0.25 in\n")
        output_file.write("}\n")
        output_file.write("\n")
        output_file.write("\\usepackage{fancyhdr}\n")
        output_file.write("\\pagestyle{fancy}\n")
        output_file.write("\\fancyhf{}\n")
        output_file.write("\\fancyhead[L]{Crush Party 2016}\n")

        def print_label (index):
            value = person1[index]
            if value != emptyID:
                output_file.write(", " + constant2string[value])

        person1name = constant2string[person1[index_of_["name"]]]
        output_file.write("\\fancyhead[R]{Results For: ")
        output_file.write(person1name + " \\\\\n")
        output_file.write("(" + netID)
        for index in index_of_["info"]:
            if type(index) is int:
                print_label(index)
            elif type(index) is list:
                for subindex in index:
                    print_label(subindex)
        output_file.write(")}\n")

        output_file.write("\n")
        output_file.write("\\begin{document}\n")
        output_file.write("\n")

        for index1 in index_of_["matches1"]:
            for index2 in index_of_["matches2"]:

                title1 = meaning_of_[tuple([index1])]
                title2 = meaning_of_[index2]

                preposition = ""
                if index2 != index_of_overall:
                    preposition = "by "

                title = "Top 10 " + title1 + " Matches " + preposition + title2
                output_file.write("\\section*{" + title + "}\n")

                output_file.write("\n")
                output_file.write("\\begin{tabular}{| l | l")
                for label in index_of_["info"]:
                    output_file.write(" | l")
                output_file.write(" |}\n")

                output_file.write("    \\hline\n")
                output_file.write("    Name & Match \\%")
                for label in index_of_["info"]:
                    output_file.write(" & " + meaning_of_[newtuple(label)])
                output_file.write(" \\\\\n")
                output_file.write("    \\hline\n")

                results = matches[person1id][index1][index2]

                for pair in results:
                    person2id = pair[0]
                    person2 = people[person2id]
                    score = int(pair[1] / num_questions * 100)

                    person2name = constant2string[person2[index_of_["name"]]]
                    output_file.write("    " + person2name + " & " + str(score))

                    for index in index_of_["info"]:

                        if type(index) is int:
                            output_file.write(" & " + 
                                    constant2string[person2[index]])

                        elif type(index) is list:
                            first = True
                            for subindex in index:
                                word = constant2string[person2[subindex]]
                                if len(word) != 0:
                                    if first:
                                        first = False
                                        output_file.write(" & ")
                                    else:
                                        output_file.write(", ")
                                    output_file.write(
                                            constant2string[person2[subindex]])

                    output_file.write(" \\\\\n")

                output_file.write("    \\hline\n")
                output_file.write("\\end{tabular}\n")
                output_file.write("\n")

            output_file.write("\\newpage\n\n");
        
        output_file.write("\\end{document}\n")



### Done! ###

print("Done!")
