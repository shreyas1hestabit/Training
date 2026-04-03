import json
import os

def clean_and_profile(file_path):
    cleaned_data = []
    word_counts = []

    with open(file_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            # Combine all text for length analysis
            full_text = entry['instruction'] + entry['input'] + entry['output']
            count = len(full_text.split())
            
            # Filter: Remove very short or excessively long entries
            if 10 < count < 500: 
                cleaned_data.append(entry)
                word_counts.append(count)

    # Split into Train (80%) and Val (20%)
    split_idx = int(len(cleaned_data) * 0.8)
    train_set = cleaned_data[:split_idx]
    val_set = cleaned_data[split_idx:]

    # Save Cleaned Data
    with open('src/data/train.jsonl', 'w') as f:
        for e in train_set: f.write(json.dumps(e) + '\n')
    with open('src/data/val.jsonl', 'w') as f:
        for e in val_set: f.write(json.dumps(e) + '\n')

    # Generate Report
    with open('DATASET-ANALYSIS.md', 'w') as f:
        f.write("# Dataset Analysis Report\n")
        f.write(f"- **Total Samples:** {len(cleaned_data)}\n")
        f.write(f"- **Avg Word Count:** {sum(word_counts)/len(word_counts):.2f}\n")
        f.write(f"- **Max Length:** {max(word_counts)}\n")
        f.write(f"- **Train/Val Split:** {len(train_set)} / {len(val_set)}\n")

    print(" Cleaning complete. Files saved in /data/ and report generated in DATASET-ANALYSIS.md")

if __name__ == "__main__":
    clean_and_profile('src/data/raw_train.jsonl')