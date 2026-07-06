from app.rules.rules import rules
import nltk
from nltk.stem import WordNetLemmatizer

nltk.download("wordnet")
nltk.download("omw-1.4")


def optimize(prompt):
    lematizer = WordNetLemmatizer()
    word = [lematizer.lemmatize(word,pos="v") for word in prompt.split()]
    prompt =  (" ".join(word)).capitalize()


    role = []
    instructions = []
    for word in prompt.lower().split():
        if word in rules:
            if "role" in rules[word]:
                role.append(rules[word]["role"])
            if "instructions" in rules[word]:
                instructions.extend(rules[word]["instructions"])
    role = list(dict.fromkeys(role))
    instructions = list(dict.fromkeys(instructions))

    opt_role = "\n".join(role)
    opt_inst = "\n".join(f"-{i}" for i in instructions)
    return {
        "original_prompt":opt_role,
        "optimized_prompt":opt_inst
    }




