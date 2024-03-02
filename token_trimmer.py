import tiktoken
import json

def tiktoken_len(text):
    # Initialize the tokenizer
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

def trim_to_token_limit(query, passages, limit=510):
    # Start with the query and incrementally add passages until the limit is reached
    combined_text = query
    for passage in passages:
        if tiktoken_len(combined_text + ' ' + passage) > limit:
            break
        combined_text += ' ' + passage
    # If over the limit, we need to trim the last passage added
    if tiktoken_len(combined_text) > limit:
        tokens = tiktoken.get_encoding('cl100k_base').encode(combined_text, disallowed_special=())
        # Trim tokens from the end until we reach the limit
        combined_text = tiktoken.get_encoding('cl100k_base').decode(tokens[:limit])
    return combined_text

def process_file(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', encoding='utf-8') as outfile:
        line_number = 0
        empty_passages_count = 0  # Counter for lines with empty 'relevant_passages'
        for line in infile:
            line_number += 1
            try:
                data = json.loads(line)
                full_text = data['query'] + ' '.join(data['relevant_passages'])
                tokens = tiktoken_len(full_text)

                if tokens > 510:
                    trimmed_text = trim_to_token_limit(data['query'], data['relevant_passages'])
                    data['relevant_passages'] = trimmed_text[len(data['query'])+1:].strip()  # +1 for the space after the query
                    if not data['relevant_passages']:
                        empty_passages_count += 1
                        print(f"Line {line_number} resulted in empty 'relevant_passages' after trimming.")

                # Write the modified data to the output file
                outfile.write(json.dumps(data) + '\n')
            except json.JSONDecodeError as e:
                print(f"Skipping line {line_number} due to JSON error: {e}")

        # After processing all lines, print the total number of lines with empty 'relevant_passages'
        print(f"Total number of lines with empty 'relevant_passages': {empty_passages_count}")

# Call the function with the specified file names
process_file('input_file', 'output_file')
