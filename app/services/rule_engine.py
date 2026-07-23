from services.intent import detect_intent
from rules.rules import rules
from services.preprocess import preprocess

def rule_engine(prompt):

    optimized_promp = preprocess(prompt)
    # rules = rules

    if "role" in optimized_promp:
        return optimized_promp["role"]
    
print(rules["essay"])
print(rule_engine("on the python code"))
