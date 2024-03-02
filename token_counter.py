import tiktoken
import json

def tiktoken_len(text):
    # Initialize the tokenizer
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

def process_file(input_filename):
    with open(input_filename, 'r', encoding='utf-8') as infile:
        line_number = 0
        over_510_token_lines_count = 0  # Counter for lines with more than 510 tokens
        for line in infile:
            line_number += 1
            try:
                data = json.loads(line)  # Convert JSON string to dictionary
                full_text =  data['query'] + ' '.join(data['relevant_passages'])
                tokens = tiktoken_len(full_text)

                # Print the number of tokens for each line
                print(f"Line {line_number} has {tokens} tokens")

                if tokens > 510:
                    over_510_token_lines_count += 1
                    print(f"Line {line_number} exceeds 510 tokens: {tokens} tokens")
            except json.JSONDecodeError as e:
                print(f"Skipping line {line_number}: Unable to parse JSON. Error: {e}")
        
        # After processing all lines, print the total number of lines with more than 510 tokens
        print(f"Total number of lines with more than 510 tokens: {over_510_token_lines_count}")

# Call the function with the specified file name
process_file('file_name')
