from app.rules.initent import intent

def detect_intent(prompt):
    prompt = prompt.lower()

    for intents, keywords in intent.items():
        for keyword in keywords:
            if keyword in prompt:
                return intents
            
    return {}