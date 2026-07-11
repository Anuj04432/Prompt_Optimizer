from app.rules.intents import intent

def detect_intent(prompt):
    prompt = prompt.lower()

    prompt_intent = []

    for intents, keywords in intent.items():
        for keyword in keywords:
            if keyword in prompt:
                prompt_intent.append(intents)

    if prompt_intent:
        return {"intents":[i for i in set(prompt_intent)]}
    else:       
        return "unknown"
    

print(detect_intent("describe  the python code"))
