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

# Function to append a rule to a JSON file
def append_rule_to_json(file_path, new_rule):
    try:
        with open(file_path, 'r+') as file:
            rules = json.load(file)
            if not rules:  # Check if the list is empty
                rules.append(new_rule.to_json())
            else:
                rules.append(new_rule.to_json())
            file.seek(0)
            json.dump(rules, file, indent=4)
            print("Rule appended successfully.")
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            json.dump([new_rule.to_json()], file)
            print("New JSON file created with the rule.")
    except json.JSONDecodeError:
        with open(file_path, 'w') as file:
            json.dump([new_rule.to_json()], file)
            print("New JSON file created with the rule.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# Create a new Rule object
new_rule = Rule([
    ('X1', 'P1376', 'X2')
], ('X1', 'P31', 'Q5119'))

# Path to the JSON file
json_file_path = 'rules.json'

# Append the new rule to the JSON file
#append_rule_to_json(json_file_path, new_rule)

def get_user_input(prompt):
    return input(prompt).strip()

def create_rule_from_user_input():
    conditions = []
    
    while True:
        print("Please provide the details for a condition:")
        subject = get_user_input("1. Tell me the subject: ")
        predicate = get_user_input("2. Tell me the predicate: ")
        obj = get_user_input("3. Tell me the object: ")
        conditions.append((subject, predicate, obj))
        
        another_condition = get_user_input("4. Do you want to add another condition (yes/no)? ").lower()
        if another_condition != 'yes':
            break

    print("Now, provide the details for the conclusion:")
    conclusion_subject = get_user_input("5. Tell me the conclusion subject: ")
    conclusion_predicate = get_user_input("6. Tell me the conclusion predicate: ")
    conclusion_object = get_user_input("7. Tell me the conclusion object: ")
    conclusion = (conclusion_subject, conclusion_predicate, conclusion_object)

    return Rule(conditions, conclusion)

new_rule = create_rule_from_user_input()
print(f"Conditions: {new_rule.conditions}")
print(f"Conclusion: {new_rule.conclusion}")