from functions import *
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
            {"role": "system", "content": f"For the given text provide all concepts and relations between them. Ignore the correctnes of the text. Present the result in a python list of tuples - subject, relation, object. Add the inverse relation if possible. Please use Wikidata labels for the results. Don't use Wikidata IRIs for the result. Don't add comments."},
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
    if fact in forward_chaining_triples:
        with open("result.txt", "a") as file:
            file.write(str(triple) + "  -->  " + str(fact in forward_chaining_triples) + "\n")
    else:
         with open("result.txt", "a") as file:
            file.write(str(triple) + "  -->  " + str(fact in forward_chaining_triples) + ", because:\n" 
                                + explanations_list[index] + "\n")

print("Check result.txt")
