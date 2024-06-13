import json
    
class Rule:
    def __init__(self, conditions, conclusion):
        self.conditions = conditions  # List of condition triples
        self.conclusion = conclusion  # Single conclusion triple

    def to_json(self):
        return json.dumps({
            'conditions': self.conditions,
            'conclusion': self.conclusion
        })    

def match_condition(triple, condition, existing_vars=None):
    variables = {}
    subject, predicate, obj = triple
    
    if existing_vars is not None:
        variables.update(existing_vars)
    
    if condition[0][0] == 'X':
        if condition[0] in variables and variables[condition[0]] != subject:
            return None
        variables[condition[0]] = subject
    elif condition[0] != subject:
        return None
    
    if condition[1][0] == 'X':
        if condition[1] in variables and variables[condition[1]] != predicate:
            return None
        variables[condition[1]] = predicate
    elif condition[1] != predicate:
        return None
    
    if condition[2][0] == 'X':
        if condition[2] in variables and variables[condition[2]] != obj:
            return None
        variables[condition[2]] = obj
    elif condition[2] != obj:
        return None
    
    return variables

def apply_rule(triples, rule):
    new_facts = set()

    def recursive_match(variables, remaining_conditions):
        if not remaining_conditions:
            # All conditions are matched, create the new fact
            new_fact = []
            for element in rule.conclusion:
                if element[0] == 'X':
                    new_fact.append(variables.get(element, ""))
                else:
                    new_fact.append(element)
            new_facts.add(tuple(new_fact))
            return
        
        current_condition = remaining_conditions[0]
        for triple in triples:
            new_variables = match_condition(triple, current_condition, variables)
            if new_variables:
                recursive_match(new_variables, remaining_conditions[1:])
    
    recursive_match({}, rule.conditions)
    return new_facts

def forward_chaining(triples, rules):
    known_facts = set(triples)
    while True:
        new_facts = set()
        for rule in rules:
            new_facts |= apply_rule(known_facts, rule)
        
        if new_facts <= known_facts:  # If no new facts were added
            break
        
        known_facts |= new_facts  # Add new facts to the set of known facts
    
    return list(known_facts)

# Example usage

"""
conditions = [("X1", "P1376", "Q27")]
conclusion_triplet = ("X1", "P31", "Q53")

rule = Rule(conditions, conclusion_triplet)
rules = [rule]

triples = [("Q18", "P1376", "Q27"), ("Entity2", "P136", "Entity3")]
new_facts = forward_chaining(triples, rules)
print(new_facts)
"""


json_file_path = "rules.json"

def load_rules_from_json(json_string):
    rules = []
    try:
        rules_json = json.loads(json_string)
        for rule_str in rules_json:
            rule_json = json.loads(rule_str)  # Parse each string as a JSON object
            if isinstance(rule_json, dict) and 'conditions' in rule_json and 'conclusion' in rule_json:
                conditions = rule_json['conditions']
                conclusion = rule_json['conclusion']
                rules.append(Rule(conditions, conclusion))
            else:
                print(f"Invalid rule format: {rule_json}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return rules

rules = []

try:
    with open(json_file_path, 'r') as file:
        json_string = file.read()
        rules = load_rules_from_json(json_string)
except FileNotFoundError:
    print(f"File not found: {json_file_path}")
except Exception as e:
    print(f"An unexpected error occurred while reading the file: {e}")
   

#triples = [("Q472", "P1376", "Q219"), ("Entity2", "P136", "Entity3")]
#new_facts = forward_chaining(triples, rules)
#print(new_facts)