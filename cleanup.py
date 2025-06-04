import re

def clean_user_input(text):
    # Step 1: Protect quoted text and file paths by replacing them with placeholders
    protected = []
    def protect(match):
        protected.append(match.group(0))
        return f"__PROTECTED{len(protected)-1}__"
    
    # Protect quoted text (handles "..." and '...')
    text = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', protect, text)
    # Protect file paths (simple heuristic: sequences with / or \ and no whitespace)
    text = re.sub(r'([A-Za-z]:[\\/][^\s"\']+|[\\/][^\s"\']+)', protect, text)
    
    # Step 2: Remove stray punctuation inside words (e.g., "exa,ple" -> "example")
    # This pattern finds a word character, then a single punctuation (not - or _), then another word character
    text = re.sub(r'(?<=\w)[,.;:!?](?=\w)', '', text)
    
    # Step 3: Restore protected content
    def restore(match):
        idx = int(match.group(1))
        return protected[idx]
    text = re.sub(r'__PROTECTED(\d+)__', restore, text)
    
    return text

# # Example usage:
# print(clean_user_input('exa,ple'))                     # example
# print(clean_user_input('"This is important"'))         # "This is important"
# print(clean_user_input('C/file/pathdirectory'))        # C/file/pathdirectory
# print(clean_user_input('He said, "exa,ple" is wrong')) # He said, "exa,ple" is wrong
