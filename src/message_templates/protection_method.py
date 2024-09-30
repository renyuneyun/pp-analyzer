SYSTEM_MESSAGE = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate protection method entities in it.
You should provide the output as a list of the protection methods contained in the sentence, and their corresponding original text, following the instructions below.

Protection method entities are phrases of privacy policy segment that mention methods of protection of USER'S PERSONAL DATA, belonging to only the following categories.

1. "general-safeguard-method"
2. "User-authentication"
3. "encryptions"
4. "Access-limitation"
5. "Protection-other"

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each protection method entity. DO NOT annotate general phrases that do not provide specific data protection method.
Examples of general phrases to omit include, but are not limited to:

"appropriate measures"
"technical measures"

Please identify and annotate ALL protection method entities in the following privacy policy segment given by the user. Do no output any explanations. Your output should be in JSON format, following this schema:

[
  {
    "protection-method": "...",
    "text": "..."
  }
]
'''


SYSTEM_MESSAGE_DETAILS = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate protection method entities in it.
You should provide the output as a list of the protection methods contained in the sentence, and their corresponding original text, following the instructions below.

Protection method entities are phrases of privacy policy segment that mention methods of protection of USER'S PERSONAL DATA, belonging to only the following categories.

1. "general-safeguard-method" - general methods of safeguarding user data
2. "User-authentication" - access to data is only granted after user authentication
3. "encryptions" - data is encrypted at rest or in transit
4. "Access-limitation" - access to data is limited to certain personnel
5. "Protection-other" - other methods of data protection

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each protection method entity. DO NOT annotate general phrases that do not provide specific data protection method.
Examples of general phrases to omit include, but are not limited to:

"appropriate measures"
"technical measures"

Please identify and annotate ALL protection method entities in the following privacy policy segment given by the user. Do no output any explanations. Your output should be in JSON format, following this schema:

[
  {
    "protection-method": "...",
    "text": "..."
  }
]
'''


USER_MESSAGE_TEMPLATE = '''Please annotate the following segment:

{segment}
'''


USER_MESSAGE_TEMPLATE_SENTENCE = '''Please annotate the following segment:

{sentence}
'''