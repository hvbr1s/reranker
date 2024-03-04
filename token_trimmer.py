import tiktoken
import json

def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

def trim_to_fit(text, limit):
    # Determine if the text is within the limit
    if tiktoken_len(text) <= limit:
        return text
    # If not, trim the text to fit within the limit
    for end in range(len(text), 0, -1):
        trimmed_text = text[:end]
        if tiktoken_len(trimmed_text) <= limit:
            return trimmed_text
    return ''  # Return an empty string if no trimming is sufficient

def trim_to_token_limit(query, passages, limit=510):
    combined_text = query
    updated_passages = []
    for passage in passages:
        proposed_text = combined_text + ' ' + passage if combined_text else passage
        if tiktoken_len(proposed_text) <= limit:
            combined_text = proposed_text
            updated_passages.append(passage)
        else:
            # Try to trim the current passage to fit
            remaining_limit = limit - tiktoken_len(combined_text + ' ')
            trimmed_passage = trim_to_fit(passage, remaining_limit)
            if trimmed_passage:
                combined_text += ' ' + trimmed_passage
                updated_passages.append(trimmed_passage)
            break  # No further passages can be added without exceeding the limit
    return combined_text.strip(), updated_passages

def process_file(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', encoding='utf-8') as outfile:
        line_number = 0
        for line in infile:
            line_number += 1
            try:
                data = json.loads(line)
                trimmed_text, trimmed_passages = trim_to_token_limit(data['query'], data['relevant_passages'])
                data['relevant_passages'] = trimmed_passages

                outfile.write(json.dumps(data) + '\n')
            except json.JSONDecodeError as e:
                print(f"Skipping line {line_number} due to JSON error: {e}")

process_file('input_file', 'output_file')
