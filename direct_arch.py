"""
{
  "audio": "path_or_relative_path.mp3",
  "aya_with_tashkeel": "...",
  "tajweed_rules": {
    "word1": ["rule1", "rule2"]
  },
  "tajweed_errors": {
    "word1": ["mistake1"]
  }
}
"""
import torch
import json
from datasets import load_dataset, Audio
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig

print("GPU:", torch.cuda.get_device_name(0))
print("VRAM:", torch.cuda.get_device_properties(0).total_memory / 1e9, "GB")
DATA_PATH = "/mnt/data/data.jsonl"

dataset = load_dataset("json", data_files=DATA_PATH)

# Convert audio column to HF Audio format
dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))

print(dataset)
print("Sample keys:", dataset["train"][0].keys())

def convert_to_error_format(example):

    instruction = "Analyze the recited Quran audio and identify tajweed mistakes."

    # Format correct rules
    correct_rules_text = ""
    for word, rules in example["tajweed_rules"].items():
        correct_rules_text += f"{word}: {', '.join(rules)}\n"

    # Format labeled errors
    error_text = ""
    for word, errors in example["tajweed_errors"].items():
        error_text += f"Word '{word}': {', '.join(errors)}\n"

    input_text = f"""
Ayah:
{example['aya_with_tashkeel']}

Correct Tajweed Rules:
{correct_rules_text}
"""

    return {
        "instruction": instruction,
        "input": input_text.strip(),
        "output": error_text.strip(),
        "audio": example["audio"]
    }

dataset = dataset["train"].map(convert_to_error_format)

print("Formatted sample:")
print(dataset[0])

dataset = dataset.train_test_split(test_size=0.1, seed=42)

train_dataset = dataset["train"]
eval_dataset = dataset["test"]

print("Train size:", len(train_dataset))
print("Eval size:", len(eval_dataset))

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-Omni-3B",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
)

model.print_trainable_parameters()

def formatting_func(example):

    prompt = f"""Below is an instruction.

### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""

    return {
        "text": prompt,
        "audio": example["audio"]
    }

training_args = SFTConfig(
    output_dir="./tajweed_error_model",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    max_steps=500,
    warmup_steps=50,
    logging_steps=10,
    save_steps=100,
    eval_steps=100,
    eval_strategy="steps",
    save_total_limit=2,
    load_best_model_at_end=True,
    fp16=True,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    formatting_func=formatting_func,
    args=training_args,
    max_seq_length=2048,
)
print("Starting training...")
trainer.train()
model.save_pretrained("./tajweed_error_model_final")
tokenizer.save_pretrained("./tajweed_error_model_final")

print("Model saved successfully.")

model.eval()

sample = eval_dataset[0]

audio_input = sample["audio"]
text_prompt = f"""
Analyze the recited Quran audio and identify tajweed mistakes.

Ayah:
{sample['aya_with_tashkeel']}
"""
inputs = tokenizer(
    text=text_prompt,
    audio=audio_input["array"],
    sampling_rate=16000,
    return_tensors="pt"
).to("cuda")
outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    temperature=0.7,
)

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)