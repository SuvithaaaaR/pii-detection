import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random

# Example training data for your use case
TRAIN_DATA = [
    ("Name: SUVITHA R", {"entities": [(6, 15, "NAME")]}),
    ("Father's Name: RAMESH", {"entities": [(15, 21, "NAME")]}),
    ("Date of Birth: 31/03/2006", {"entities": [(15, 25, "DOB")]}),
    ("Permanent Account Number Card SSZPS4280P", {"entities": [(32, 42, "PAN")]}),
    ("Aadhaar: 1234-5678-9012", {"entities": [(9, 23, "AADHAAR")]}),
    ("Email: test@example.com", {"entities": [(7, 23, "EMAIL")]}),
    ("Phone: 123-456-7890", {"entities": [(7, 19, "PHONE")]}),
    ("DOB: 01/01/1990", {"entities": [(5, 15, "DOB")]}),
    ("Name: Rahul Sharma", {"entities": [(6, 18, "NAME")]}),
    ("PAN: ABCDE1234F", {"entities": [(5, 15, "PAN")]}),
]

# Create blank English model
nlp = spacy.blank("en")
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# Add custom entity labels
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipes for training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for itn in range(30):
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.5))
        for batch in batches:
            for text, annotations in batch:
                example = Example.from_dict(nlp.make_doc(text), annotations)
                nlp.update([example], drop=0.5, losses=losses)
        print(f"Iteration {itn+1}, Losses: {losses}")

# Save the trained model
nlp.to_disk("custom_pii_ner_model")
print("Model saved to custom_pii_ner_model/")
