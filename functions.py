import asyncio
import requests
from rule import *

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

    return file_content

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
        "type": entity_type,
        "limit": 10
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['search']:
        for entity in data['search']:
            if entity.get('label', '') == label:
                return entity['id']
    return None

def map_triple_to_wikidata(triple):
    subject_id = search_wikidata_entity(triple[0], "item")
    predicate_id = search_wikidata_entity(triple[1], "property")
    object_id = search_wikidata_entity(triple[2], "item")
    
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

def get_wikidata_label(wikidata_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        entity = data['entities'][wikidata_id]
        label = entity['labels']['en']['value']
        return label
    else:
        return None

def format_wikidata_objects(wikidata_ids):
    formatted_objects = []
    for wikidata_id in wikidata_ids:
        label = get_wikidata_label(wikidata_id)
        if label:
            formatted_objects.append(f"{wikidata_id}({label})")
        else:
            formatted_objects.append(f"{wikidata_id}(No Label Found)")
    return formatted_objects

def check_wikidata_relationship(triple):
    subject_id = triple[0][1]
    predicate_id = triple[1][1]
    object_id = triple[2][1]

    claim_ids = get_claim_ids(subject_id, predicate_id)
    if not claim_ids:
        return False, f"No claims found for subject ID '{subject_id}'({triple[0][0]}) with predicate ID '{predicate_id}'({triple[1][0]})."
    
    if object_id not in claim_ids:
        return False, f"Object ID '{object_id}'({triple[2][0]}) not found among claims for subject ID '{subject_id}'({triple[0][0]}) with predicate ID '{predicate_id}'({triple[1][0]}). Available claim IDs: {format_wikidata_objects(claim_ids)}."
    
    return True, "The relationship is correct."
