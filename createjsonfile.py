import json
import glob
import os
import pandas as pd
import re
from  tajweed_rule import extract_tajweed_rules
# function to remove tashkeel
def remove_tashkeel(text):
    tashkeel = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return re.sub(tashkeel, '', text)

data_aya = pd.read_csv("archive/The Quran Dataset.csv")
with open("data.jsonl", "w", encoding="utf-8") as json_file:
    for i, folderpath in enumerate(sorted(glob.glob("dataset/*"))): 
        print(f"Processing folder: {folderpath}")
        for j, filepath in enumerate(sorted(glob.glob(folderpath+"/*"))):
            print(f"Processing file: {filepath}")
            aya_with_tashkeel = data_aya.iloc[j]["ayah_ar"]
            aya_without_tashkeel = remove_tashkeel(aya_with_tashkeel)
            data = {
                "audio": filepath,
                "aya_with_tashkeel": str(aya_with_tashkeel),
                "aya_without_tashkeel": str(aya_without_tashkeel),
                "surah_name": str(data_aya.iloc[j]["surah_name_roman"]),
                "ayah": int(data_aya.iloc[j]["ayah_no_surah"]),  # convert to Python int
                "reciter": folderpath.split(os.sep)[-1] , # extract reciter name from folder path
                "tajweed_rules": extract_tajweed_rules(aya_with_tashkeel)  # extract tajweed rules
            }

            json_file.write(json.dumps(data, ensure_ascii=False) + "\n")
