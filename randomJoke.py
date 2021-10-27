import random

# All these are random dad jokes from google, comedy quality not taken in account
jokes=[
'Which bear is the most condescending? A pan-duh!',
'What kind of noise does a witch’s vehicle make? Brrrroooom, brrroooom.',
'What’s brown and sticky? A stick.',
'Two guys walked into a bar. The third guy ducked.',
'How do you get a country girl’s attention? A tractor.',
'Why are elevator jokes so classic and good? They work on many levels.',
'What do you call a pudgy psychic? A four-chin teller.',
'What did the police officer say to his belly-button? You’re under a vest.',
'What do you call it when a group of apes starts a company? Monkey business.',
'My wife asked me to stop singing “Wonderwall” to her. I said maybe…'
]

# Returns a random joke from array to the caller which calls it
def someJoke():
    return random.choice(jokes)
