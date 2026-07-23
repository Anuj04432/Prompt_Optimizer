from services.intent import detect_intent

def optimized_prompt(prompt):
    words = []
    for i in prompt.split():
        words.append(i)
        
    if len(words) < 3:
        return "What you mean?"
    
    else:
        intent = detect_intent(prompt)
        if intent!="unknown":
            word = [k for k in intent["intents"]]
            return word
        else:
            return "unknown"

        

          

        
    
