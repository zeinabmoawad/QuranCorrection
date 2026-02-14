import json
import glob
import os
import pandas as pd
import re

# function to remove tashkeel
def remove_tashkeel(text):
    tashkeel = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return re.sub(tashkeel, '', text)

data_aya = pd.read_csv("archive/The Quran Dataset.csv")
with open("data.jsonl", "w", encoding="utf-8") as json_file:
    for i, filepath in enumerate(sorted(glob.glob("surah_001/*"))):
        
        aya_with_tashkeel = data_aya.iloc[i]["ayah_ar"]
        aya_without_tashkeel = remove_tashkeel(aya_with_tashkeel)

        data = {
            "audio": filepath,
            "aya_with_tashkeel": str(aya_with_tashkeel),
            "aya_without_tashkeel": str(aya_without_tashkeel),
            "surah_name": str(data_aya.iloc[i]["surah_name_roman"]),
            "ayah": int(data_aya.iloc[i]["ayah_no_surah"]),  # convert to Python int
            "reciter": "Husary"
        }

        json_file.write(json.dumps(data, ensure_ascii=False) + "\n")
