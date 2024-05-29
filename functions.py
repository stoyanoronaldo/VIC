import asyncio
import requests

def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

def get_answer_from_file(file_name):
    with open(file_name, 'r') as file:
        file_content = file.read()

    start_index = file_content.find("```")
    end_index = file_content.find("```", start_index + 1)
    extracted_text = file_content[start_index + 3:end_index].strip()

    return extracted_text

def get_answer_from_string(str):
    start_index = str.find("```")
    end_index = str.find("```", start_index + 1)
    extracted_text = str[start_index + 3:end_index].strip()

    return extracted_text

def save_answer_to_file(answer, file_path):
    with open(file_path, 'w') as file:
        file.write(answer)

def search_wikidata_entity(label, entity_type="item"):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": label,
        "language": "en",
        "format": "json",
        "type": entity_type
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['search']:
        return data['search'][0]['id']
    return None

def map_triple_to_wikidata(triple):
    subject_id = search_wikidata_entity(triple[0], "item")
    predicate_id = search_wikidata_entity(triple[1], "property")
    object_id = search_wikidata_entity(triple[2], "item")
    
    if not subject_id:
        print(f"Could not find a Wikidata entity for subject '{triple[0]}'.")
    if not predicate_id:
        print(f"Could not find a Wikidata property for predicate '{triple[2]}'.")
    if not object_id:
        print(f"Could not find a Wikidata entity for object '{triple[1]}'.")
    
    return (subject_id, predicate_id, object_id)

def merge_triples(original_triples, mapped_triples):
    merged_triples = []
    for orig, mapped in zip(original_triples, mapped_triples):
        merged_triple = tuple(zip(orig, mapped))
        merged_triples.append(merged_triple)

    return merged_triples

def get_claim_ids(entity_id, property_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        claims = data.get('entities', {}).get(entity_id, {}).get('claims', {}).get(property_id, [])
        return [claim['mainsnak']['datavalue']['value']['id'] for claim in claims if 'mainsnak' in claim and 'datavalue' in claim['mainsnak'] and 'value' in claim['mainsnak']['datavalue'] and 'id' in claim['mainsnak']['datavalue']['value']]
    return []

def check_wikidata_relationship(triple):
    subject_id = triple[0][1]
    predicate_id = triple[1][1]
    object_id = triple[2][1]

    claim_ids = get_claim_ids(subject_id, predicate_id)
    if object_id in claim_ids:
        return True
    return False
