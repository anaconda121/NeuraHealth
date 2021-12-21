import csv
import json
from pathlib import Path
from faker import Faker
import random
from datetime import datetime, timedelta

directory = Path(__file__).parent

fake = Faker()

patients = 406
patient_ids = [fake.unique.ean(length=13) for _ in range(patients)]

first_date = datetime(year=2000, month=1, day=1)

rows = []
for patient_id in patient_ids:
    encounter_ids = [
        fake.unique.ean(length=8)
        for _ in range(random.randint(1, 5))
    ]
    for encounter_id in encounter_ids:
        note_ids = [fake.unique.ean(length=13) for _ in range(random.randint(1, 3))]
        days = random.randint(40, 4586)
        date = (
            first_date + timedelta(days=days)
        )
        date = date.strftime("%Y-%m-%d")
        for note_id in note_ids:
            for sentence in [fake.paragraph(nb_sentences=4) for _ in range(random.randint(1, 3))]:
                words = sentence.split()
                num_matches = random.randint(1, len(words))
                regex_matches = random.choices(words, k=num_matches)
                row = {
                    "PatientID": patient_id,
                    "MRN": patient_id,
                    "EMPI": patient_id,
                    "PatientEncounterID": encounter_id,
                    "NoteID": note_id,
                    "ContactDTS": date,
                    "regex_sent": json.dumps(sentence),
                    "regex_match": json.dumps(regex_matches)
                }
                rows.append(row)

with open(directory / "test_data.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows")



