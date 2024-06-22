import json

synonyms_file_path = "synonyms.json"

def load_synonyms(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return {}

def save_synonyms(file_path, synonyms):
    with open(file_path, 'w') as file:
        json.dump(synonyms, file, indent=4)

def add_synonym(file_path, word, synonym):
    synonyms = load_synonyms(file_path)
    if word in synonyms:
        synonyms[word].append(synonym)
    else:
        synonyms[word] = [synonym]
    save_synonyms(file_path, synonyms)

def get_synonyms(file_path, word):
    synonyms = load_synonyms(file_path)
    return synonyms.get(word, [])

def add_synonyms_interactively(file_path):
    while True:
        word = input("Enter the word: ").strip()
        synonym = input(f"Enter a synonym for '{word}': ").strip()
        add_synonym(file_path, word, synonym)
        another = input("Do you want to add another synonym (yes/no)? ").strip().lower()
        if another != 'yes':
            break

# Example usage
add_synonyms_interactively(synonyms_file_path)

# Print the synonyms dictionary
synonyms = load_synonyms(synonyms_file_path)
print("Synonyms dictionary:")
print(synonyms)
