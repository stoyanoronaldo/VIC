from functions import *
from add_synonyms import *
import ast

# Ensure an event loop is created before importing llamaapi
loop = get_or_create_event_loop()

# Now you can safely import llamaapi
from llamaapi import LlamaAPI

chatbot_on = True
answer = ''

if chatbot_on:
    user_input = input("Enter some text: ")

    llama = LlamaAPI("LL-oZZ3DbV8EBPzVAdh7ylv5pQP3y0ryH77l7x50ELwEzDymcHuVOA3BnhH66HdFIZh")

    api_request_json = {
        "model": "llama3-70b",
        "max_tokens": 10000,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": f"For the given text provide all concepts and relations between them. Ignore the correctnes of the text. Present the result in a python list of tuples - subject, relation, object. Please use Wikidata labels for the results. Don't use Wikidata IRIs for the result. Don't add comments."},
            {"role": "user", "content": f"Text: {user_input}"},
        ]
    }

    while True:
        try:
            response = llama.run(api_request_json)
            response.raise_for_status()
            answer_content = response.json()["choices"][0]["message"]["content"]
            break
        except requests.exceptions.JSONDecodeError as e:
            print(f"Error: {e}")

    save_answer_to_file(answer_content, 'response.txt')
    answer = answer_content
else:
    answer = get_answer_from_file("response.txt")

triples_list = eval(answer)

wikidata_mappings = []
for triple in triples_list:
    wikidata_mappings.append(map_triple_to_wikidata(triple))

merged_triples = merge_triples(triples_list, wikidata_mappings)

true_triples = []
explanations_list = []
for triple in merged_triples:
    is_true_triple, explanation = check_wikidata_relationship(triple)
    explanations_list.append(explanation)
    if is_true_triple:
        new_triple = (triple[0][1], triple[1][1], triple[2][1]) 
        true_triples.append(new_triple)
    else:
       synonyms = get_synonyms(synonyms_file_path, triple[1][0])
       for synonym in synonyms:
        new_triple = (triple[0][0], synonym, triple[2][0])
        new_triple_map = map_triple_to_wikidata(new_triple)
        mapped_triple = tuple(zip(new_triple, new_triple_map))
        is_true_triple, explanation = check_wikidata_relationship(mapped_triple)
        if is_true_triple:
            true_triples.append(mapped_triple)
            explanations_list[-1] = explanation
            break
        else:
            explanations_list[-1] = explanations_list[-1] + "\nAND\n" + explanation


with open("triples.txt", "w") as file:
    file.write(str(merged_triples))

#print(true_triples)

forward_chaining_triples = forward_chaining(true_triples, rules)

with open("result.txt", "w") as file:
    pass

#print(forward_chaining_triples) 
for index, triple in enumerate(merged_triples):
    subject = triple[0][1]
    predicate = triple[1][1]
    obj = triple[2][1]
    fact = (subject, predicate, obj)
    output_str = f"{triple[0][0]} {triple[1][0]} {triple[2][0]}"
    if fact in forward_chaining_triples or explanations_list[index] == "The relationship is correct.":
        with open("result.txt", "a") as file:
            file.write(output_str + "  -->  True\n\n")
    else:
         with open("result.txt", "a") as file:
            file.write(output_str + "  --> False, because:\n" + explanations_list[index] + "\n\n")

print("Check result.txt")
