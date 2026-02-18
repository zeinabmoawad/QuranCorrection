# from datasets import load_dataset

# dataset = load_dataset("json", data_files="data.jsonl")
# dataset = load_dataset("ZeinabMoawad/quran-dataset")

# print(dataset["train"][0])
from datasets import load_dataset, Features, Value, Audio

features = Features({
    "audio": Audio(sampling_rate=16000),
    "aya_with_tashkeel": Value("string"),
    "aya_without_tashkeel": Value("string"),
    "surah_name": Value("string"),
    "ayah": Value("int32"),
    "reciter": Value("string"),
})

dataset = load_dataset("json", data_files="train.jsonl", features=features)
dataset.push_to_hub("ZeinabMoawad/quran-dataset")

