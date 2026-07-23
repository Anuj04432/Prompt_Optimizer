from rules.intents import intent
from services.preprocess import preprocess

def detect_intent(prompt):
    prompt = preprocess(prompt)

    language = ["python","english","java","marathi","javascript","html","css","php","sql","hindi","kannada","telegu"]
    task = ["coding","writing","thinking","analyzing","building","explaining","debugging","learning","reading","writing","researching","designing","testing","reviewing","collaborating","communicating"]



    prompt_intent = []

    for intents, keywords in intent.items():
        for keyword in keywords:
            if keyword in prompt:
                prompt_intent.append(intents)

    if prompt_intent:
        return {"intents":[i for i in set(prompt_intent)]}
    else:       
        return "unknown"
    
    


