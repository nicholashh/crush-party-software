
import csv

def match ():

    with open('data.csv', 'r', encoding='utf-8') as data_file:
        with open('format.txt', 'r') as format_file:

            ### STEP 1: Parse the format file. ###

            index_of_ = {}
            meaning_of_ = {}

            for row in format_file:
                row = row.strip()

                if row == "": continue

                format_entry = row.split(":")
                key = format_entry[0]
                value = format_entry[1].split(" ")[1:]

                def char_to_index (char_array):
                    # create the array of indices to output
                    index_array = []
                    # for each column in the format key
                    for column in char_array:
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

                valid_keys = ["name", "email", "gender", 
                        "matches", "information", "questions"]

                if key in valid_keys:
                    index_of_[key] = char_to_index(value)

                elif len(key) == 1:
                    meaning_of_[char_to_index(key)[0]] = value[0]

            name_index = index_of_["name"][0]
            gender_index = index_of_["gender"][0]
            matches_indices = index_of_["matches"]
            questions_indices = index_of_["questions"]
            num_questions = len(questions_indices)

            # print(index_of_)
            # print(meaning_of_)

            ### STEP 2: Parse the data file. ###

            people = {}

            string_to_int = {}
            int_to_string = {}
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
                    if term not in string_to_int:
                        string_to_int[term] = constant
                        int_to_string[constant] = term
                        constant += 1
                    answers.append(string_to_int[term])

                if len(answers) != expected_num_answers:
                    print("oops")
                    continue

                people[answers[name_index]] = tuple(answers)

            # print(people)
            # print(string_to_int)

            ### STEP 3: Compute similarity scores. ###

            similarity_scores = {}

            for person1id in people:
                for person2id in people:
                    if person1id != person2id:

                        person1 = people[person1id]
                        person2 = people[person2id]
                        score = 0

                        for answer in questions_indices:
                            if person1[answer] == person2[answer]:
                                score += 1

                        names1 = (person1[name_index], person2[name_index])
                        names2 = (names1[1], names1[0])
                        similarity_scores[names1] = score
                        similarity_scores[names2] = score

            print(similarity_scores)

            ### STEP 4: Compute compatible matches. ###

            matches = {}

            for person1id in people:
                person1 = people[person1id]
                new_matches_results = {}
                for match_index in matches_indices:
                    new_matches_list = []
                    for pair in similarity_scores:
                        if pair[0] == person1id:
                            person2id = pair[1]
                            person2 = people[person2id]
                            score = similarity_scores[pair]
                            
                            person1gender = int_to_string[person1[gender_index]]
                            person2gender = int_to_string[person2[gender_index]]

                            person1options = int_to_string[person1[match_index]]
                            person2options = int_to_string[person2[match_index]]

                            if person2gender in person1options:
                                if person1gender in person2options:
                                    new_matches_list.append((person2id, score))

                    new_matches_results[match_index] = new_matches_list
                matches[person1id] = new_matches_results

            print(matches)

            ### STEP 5: Compute best matches. ###

            for person1id in matches:
                for match_index in matches_indices:
                    matches[person1id][match_index].sort(key = lambda x: -x[1])
                    matches[person1id][match_index] = \
                            matches[person1id][match_index][:10]

            print(matches)

            ### STEP 6: Output best matches. ###

            for person1id in matches:
                print("matches for " + int_to_string[person1id] + ":")
                for match_index in matches_indices:
                    print("    " + meaning_of_[match_index] + " matches:")
                    for match in matches[person1id][match_index]:
                        print("        " + int_to_string[match[0]] + \
                                " (" + str(match[1] / num_questions) + ")")

match()
