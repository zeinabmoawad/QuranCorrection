# # Quran Tajweed Rules Fine-tuning on T4 GPU
# Complete solution optimized for Google Colab T4 (15GB VRAM)

# Install required packages (run once)
#!pip install -q unsloth transformers datasets trl peft accelerate bitsandbytes
#!pip install -q xformers trl

import torch
import json
import random
from datasets import Dataset
# from transformers import (
#     AutoTokenizer, 
#     BitsAndBytesConfig,
#     TrainingArguments
# )
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig, get_peft_model, TaskType

# Check GPU
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# Load your JSON data
def load_json_data(file_path):
    """Load JSONL data from file"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def convert_to_instruction_format(data):
    """Convert raw data to instruction format with varied prompts"""
    formatted_data = {
        "instruction": [],
        "input": [],
        "output": []
    }
    
    # instructions_pool = [
    #     "List all tajweed rules present in this Quranic verse.",
    #     "Analyze the tajweed rules for each word in the following verse.",
    #     "What are the tajweed rules applicable to this verse?",
    #     "Provide a word-by-word tajweed rule analysis for this Quranic verse.",
    #     "Identify and explain the tajweed rules in this verse.",
    #     "Break down the tajweed rules for each word in this ayah.",
    #     "Give me the tajweed rulings for every word in this verse.",
    #     "Perform a tajweed analysis of this Quranic verse.",
    #     "What tajweed rules can be found in this ayah?",
    #     "Extract and list all tajweed rules from this verse word by word."
    # ]
    
    for item in data:
        # instruction = random.choice(instructions_pool)
        instruction = "Identify and explain the tajweed rules in this verse."
        
        if random.random() > 0.5:
            input_text = f"Surah {item['surah_name']}, Ayah {item['ayah']} recited by {item['reciter']}: {item['aya_with_tashkeel']}"
        else:
            input_text = f"{item['aya_with_tashkeel']}"
        
        output_text = ""
        for word, rules in item['tajweed_rules'].items():
            output_text += f"Word '{word}': {', '.join(rules)}\n"
        
        formatted_data["instruction"].append(instruction)
        formatted_data["input"].append(input_text)
        formatted_data["output"].append(output_text.strip())
    
    return formatted_data

# Load and prepare dataset
json_file = "./data.jsonl"  # Update this path
print("Loading data...")
raw_data = load_json_data(json_file)
print(f"Loaded {len(raw_data)} samples")

# Convert to instruction format
print("Converting to instruction format...")
formatted_data = convert_to_instruction_format(raw_data)

# Create HuggingFace dataset
dataset = Dataset.from_dict(formatted_data)

# Split into train/validation
split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split_dataset["train"]
val_dataset = split_dataset["test"]

print(f"Train samples: {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")
print("\nSample:")
print(f"Instruction: {train_dataset[0]['instruction']}")
print(f"Input: {train_dataset[0]['input']}")
print(f"Output: {train_dataset[0]['output']}")

# OPTION 1: Use a smaller model that fits T4 (Recommended for stability)
print("\n" + "="*50)
print("OPTION 1: Loading smaller Qwen2-1.5B model...")
print("="*50)

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2-1.5b-bnb-4bit",  # 1.5B parameter version
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
    device_map="auto",
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
    max_seq_length=2048,
)


# Use Qwen2-7B with CPU offloading (if you really need 7B)
"""
print("\n" + "="*50)
print("OPTION 2: Loading Qwen2-7B with CPU offloading...")
print("="*50)

# Quantization config with CPU offloading enabled
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    llm_int8_enable_fp32_cpu_offload=True,  # CRITICAL: Enable CPU offloading
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "unsloth/Qwen2-7b-bnb-4bit",
    trust_remote_code=True
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Load model with custom device map and memory limits
model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Qwen2-7b-bnb-4bit",
    quantization_config=quantization_config,
    device_map="auto",  # Let accelerate handle distribution
    trust_remote_code=True,
    max_memory={
        0: "12GiB",     # Use 12GB of GPU memory
        "cpu": "20GiB"  # Use 20GB of CPU RAM for offloading
    },
    offload_folder="offload_folder",  # For disk offloading if needed
)

# Add LoRA adapters
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,  # Lower rank to save memory
    lora_alpha=16,
    lora_dropout=0.1,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    bias="none",
)
model = get_peft_model(model, lora_config)
"""


# Print trainable parameters
print("\nTrainable parameters:")
model.print_trainable_parameters()


# Create formatting function for SFTTrainer
def create_formatting_function(tokenizer):
    alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""
    
    EOS_TOKEN = tokenizer.eos_token
    
    def formatting_prompts_func(examples):
        texts = []
        
        if isinstance(examples, dict):
            instructions = examples.get("instruction", [])
            inputs = examples.get("input", [])
            outputs = examples.get("output", [])
            
            for instruction, input_text, output in zip(instructions, inputs, outputs):
                text = alpaca_prompt.format(instruction, input_text, output) + EOS_TOKEN
                texts.append(text)
        else:
            instruction = examples["instruction"]
            input_text = examples["input"]
            output = examples["output"]
            text = alpaca_prompt.format(instruction, input_text, output) + EOS_TOKEN
            texts.append(text)
        
        return texts
    
    return formatting_prompts_func

formatting_func = create_formatting_function(tokenizer)


# Configure training arguments 
training_args = SFTConfig(
    output_dir="./quran_tajweed_model",
    
    # Batch sizes optimized 
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,  # Effective batch size = 8
    
    # Memory optimizations
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    fp16=True,
    
    # Training steps (adjust based on your needs)
    max_steps=500,
    warmup_steps=50,
    learning_rate=2e-4,
    
    # Logging and saving
    logging_steps=10,
    save_steps=100,
    eval_steps=100,
    eval_strategy="steps",
    save_total_limit=2,
    load_best_model_at_end=True,
    
    # Other settings
    report_to="none",
    remove_unused_columns=False,
    dataloader_num_workers=2,
)


# Initialize trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    formatting_func=formatting_func,
    args=training_args,
    max_seq_length=2048,
)


# Start training
print("\n" + "="*50)
print("Starting training...")
print("="*50)
trainer.train()


# Save the model
print("\nSaving model...")
model.save_pretrained("./quran_tajweed_model_final")
tokenizer.save_pretrained("./quran_tajweed_model_final")

print("\n Training complete! Model saved to './quran_tajweed_model_final'")


# Test the model
print("\n" + "="*50)
print("Testing the model...")
print("="*50)

model.eval()

test_instruction = "List all tajweed rules present in this Quranic verse."
test_input = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"

prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{test_instruction}

### Input:
{test_input}

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    temperature=0.7,
    do_sample=True,
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)