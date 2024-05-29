from functions import *
import ast

# Ensure an event loop is created before importing llamaapi
loop = get_or_create_event_loop()

# Now you can safely import llamaapi
from llamaapi import LlamaAPI

chatbot = False

if chatbot:
    user_input = input("Please enter something: ")

    llama = LlamaAPI("LL-0GnzCST2ctEjinWEhaiT7ErxjRrZ4SfMq4hSsNWT3YNjynq8SZCDNdWbblwULzVK")

    api_request_json = {
        "model": "llama3-70b",
        "messages": [
            {"role": "system", "content": f"For the given text provide all concepts and relations between them. Present the result in a python triple - subject, predicate, object."},
            {"role": "user", "content": f"Text: {user_input}"},
        ]
    }

    response = llama.run(api_request_json)
    answer_content = response.json()["choices"][0]["message"]["content"]
    save_answer_to_file(answer_content, 'response.txt')
    answer = get_answer_from_string(answer_content)
else:
    answer = get_answer_from_file("response.txt")

triples_str = answer.split('=')[1].strip()
triples_list = ast.literal_eval(triples_str)

wikidata_mappings = []
for triple in triples_list:
    wikidata_mappings.append(map_triple_to_wikidata(triple))

merged_triples = merge_triples(triples_list, wikidata_mappings)

for triple in merged_triples:
    print(str(triple) + "  -->  " + str(check_wikidata_relationship(triple)))



