
import csv

def match ():

    with open('data.csv', 'r', encoding='utf-8') as data_file, \
            open('format.txt', 'r') as format_file:

        ### STEP 1: Parse the format file. ###

        index_of_ = {}
        meaning_of_ = {}

        for row in format_file:

            row = row.strip()

            if row == "": continue

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

            format_entry = row.split(":")
            key = format_entry[0]
            value = format_entry[1]

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

        new_matches2_index = []
        for index in index_of_["matches2"]:
            if type(index) is list:
                index = tuple(index)
            elif type(index) is int:
                index = tuple([index])
            new_matches2_index.append(index)
        index_of_["matches2"] = new_matches2_index

        print("index_of_")
        print(index_of_)
        print("meaning_of_")
        print(meaning_of_)

        ### STEP 2: Parse the data file. ###

        people = {}

        string2constant = {}
        constant2string = {}
        constant = 0

        i = 0
        expected_num_answers = 0;
        for row in csv.reader(data_file):
            i += 1
            if i == 1:
                expected_num_answers = len(row)
                continue
            # if i >= 10: break

            answers = []
            for term in row:
                if term not in string2constant:
                    string2constant[term] = constant
                    constant2string[constant] = term
                    constant += 1
                answers.append(string2constant[term])

            if len(answers) != expected_num_answers:
                print("oops")
                continue

            people[answers[index_of_["name"]]] = tuple(answers)

        print("people")
        print(people)

        ### STEP 3: Compute similarity scores. ###

        similarity_scores = {}

        for person1id in people:
            for person2id in people:
                if person1id != person2id:

                    person1 = people[person1id]
                    person2 = people[person2id]
                    score = 0

                    for answer in index_of_["questions"]:
                        if person1[answer] == person2[answer]:
                            score += 1

                    names1 = (person1[index_of_["name"]], person2[index_of_["name"]])
                    names2 = (names1[1], names1[0])
                    similarity_scores[names1] = score
                    similarity_scores[names2] = score

        ### STEP 4: Compute compatible matches. ###

        matches = {}

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

                        person1options = constant2string[person1[index1]]
                        person2options = constant2string[person2[index1]]

                        if person2gender in person1options:
                            if person1gender in person2options:
                                new_matches_list.append((person2id, score))

                new_matches_results[index1] = {}
                new_matches_results[index1][-1] = new_matches_list

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
                            for value2 in persion2values:
                                if value1 == value2:
                                    compatible = True

                        if compatible:
                            new_matches_list.append(pair)

                    new_matches_results[index1][index2] = new_matches_list

            matches[person1id] = new_matches_results

        ### STEP 5: Compute best matches. ###

        for person1id in matches:
            for index1 in index_of_["matches1"]:
                for index2 in index_of_["matches2"]:
                    matches[person1id][index1][index2] = sorted(
                            matches[person1id][index1][index2],
                            key = lambda pair: -pair[1])[:10]

        print("matches")
        print(matches)

        ### STEP 6: Output best matches. ###

        num_questions = len(index_of_["questions"])

        # for person1id in matches:
        #     print("matches for " + constant2string[person1id] + ":")
        #     for match_index in index_of_["matches1"]:
        #         print("    " + meaning_of_[match_index] + " matches:")
        #         for match in matches[person1id][match_index]:
        #             print("        " + constant2string[match[0]] + \
        #                     " (" + str(match[1] / num_questions) + ")")

#         def output_one_page (person, matches, i):

#             netID = person[index_of_["email"]].split("@")[0]
#             with open('./results/'+netID+'.'+i+'.tex', 'w') as output_file:

#                 output_file.write("\n");
#                 output_file.write("\\documentclass[a4paper]{article}\n");
#                 output_file.write("\n");
#                 output_file.write("\\usepackage[english]{babel}\n");
#                 output_file.write("\\usepackage[utf8]{inputenc}\n");
#                 output_file.write("\\usepackage{parskip}\n");
#                 output_file.write("\n");
#                 output_file.write("\\usepackage{geometry}\n");
#                 output_file.write("\\geometry{\n");
#                 output_file.write("    tmargin   = 1.5 in,\n");
#                 output_file.write("    lmargin   = 1.00 in,\n");
#                 output_file.write("    rmargin   = 1.00 in,\n");
#                 output_file.write("    bmargin   = 1.00 in,\n");
#                 output_file.write("    headheight  = 0.50 in,\n");
#                 output_file.write("    headsep   = 0.25 in\n");
#                 output_file.write("}\n");
#                 output_file.write("\n");
#                 output_file.write("\\usepackage{fancyhdr}\n");
#                 output_file.write("\\pagestyle{fancy}\n");
#                 output_file.write("\\fancyhf{}\n");
#                 output_file.write("\\fancyhead[L]{Crush Party 2016}\n");

#                 # output_file.write("\\fancyhead[R]{Results For: " + person.getName() + " \\\\\n");
#                 # output_file.write("(" + person.getGender() + ", " + person.getYear() +
#                 #         ", " + person.getCollege() + ", " + person.getMajor() + ")}\n");

#                 output_file.write("\n");
#                 output_file.write("\\begin{document}\n");
#                 output_file.write("\n");
#                 output_file.write("\\section*{Best Results}\n");
#                 output_file.write("\n");
#                 writeOneTable(document, person, "List 1", 0);
#                 writeOneTable(document, person, "List 2", 2);
#                 writeOneTable(document, person, "List 3", 4);
#                 output_file.write("\\newpage\n");
#                 output_file.write("\\section*{Worst Results}\n");
#                 output_file.write("\n");
#                 writeOneTable(document, person, "List 1", 1);
#                 writeOneTable(document, person, "List 2", 3);
#                 writeOneTable(document, person, "List 3", 5);
#                 output_file.write("\\end{document}\n");

#     }

#     private static void writeOneTable (PrintWriter document, Student person,
#                                   String listName, int index) {

#         List<Student> matches = person.getMatchesForList(index);

#         output_file.write("\\subsection*{" + listName + "}\n");
#         output_file.write("\n");
#         output_file.write(person.getDescriptionForList(index) + " \\\\\n");
#         output_file.write("\n");
#         output_file.write("\\begin{tabular}{| l | l | l | l | l | l |}\n");
#         output_file.write("    \\hline\n");
#         output_file.write("    Name & Match & Gender & Year & College & Major \\\\\n");
#         output_file.write("    \\hline\n");
#         for (int i = 0; i < 10; i++) {
#             Student match = matches.get(i);
#             String gen;
#             if (match.getGender() != null && match.getGender() == Gender.NOTHING) {
#                 gen = "";
#             } else if (match.getGender() != null) {
#                 String genA = match.getGender().toString().substring(0, 1);
#                 String genB = match.getGender().toString().substring(1).toLowerCase();
#                 gen = genA + genB;
#             } else {
#                 gen = "";
#             }

#             output_file.write("    " + i + ". " + match.getName() + " \n& "
#                     + Math.round(person.getPercentagesForList(index).get(i) * 100) + "\\% & "
#                     + gen + " & " + match.getYear() + " & "
#                     + match.getCollege() + " & " + match.getMajor() + " \\\\");
#         }
#         output_file.write("    \\hline\n");
#         output_file.write("\\end{tabular}\n");
#         output_file.write("\n");

#     }

# }


match()
