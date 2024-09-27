SYSTEM_MESSAGE = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate actions in it.

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each potential data entity. DO NOT annotate sentences that do not provide specific data types or purpose types.
Examples of general phrases to omit include, but are not limited to:

"the information we collect about you"
"other data"
"any information"
"other purposes"
"purposes described in our policy"

If a sentence does not clearly indicate a specific type of personal data, DO NOT include it in your annotations.

Data usage context refers to the (core phrases within) sentences that mention the actions that are being taken with the PERSONAL DATA OF THE USER which is being mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

Note the following!
1. Personal user data that is mentioned outside of one of these contexts does not classify as data entity.
2. Multiple contexts may apply to the same data entity.
3. Tracking technologies such as cookies, web beacons, etc. are technologies, hence does not classify as data entity and should NOT be annotated.
4. The policy segment that you receive might be empty or not contain any information on usage of concrete personal user data - that's normal, and you should just return an empty list.

Provide the output as a list of data usage contexts with the following details for each entry:
1. The type of the context as in one of the five context types mentioned above.
2. The exact text of the context as it appears in the text segment.
3. The exact sentence of the context as it appears in the text segment.

You will be given the segment below from user input. Please identify and annotate ALL data usage contexts in the following privacy policy segment.
Your output should follow this JSON structure:

[
    {
        "action_type": "...",
        "text": "...",
        "sentence": "..."
    },
    {
        "action_type": "...",
        "text": "...",
        "sentence": "..."
    }
]
'''


USER_MESSAGE_TEMPLATE = '''Please annotate the following segment:

{segment}
'''


SYSTEM_MESSAGE_SENTENCE = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate actions in it.

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each potential data entity. DO NOT annotate sentences that do not provide specific data types or purpose types.
Examples of general phrases to omit include, but are not limited to:

"the information we collect about you"
"other data"
"any information"
"other purposes"
"purposes described in our policy"

If a sentence does not clearly indicate a specific type of personal data, DO NOT include it in your annotations.

Data usage context refers to the (core phrases within) sentences that mention the actions that are being taken with the PERSONAL DATA OF THE USER which is being mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

Note the following!
1. Personal user data that is mentioned outside of one of these contexts does not classify as data entity.
2. Multiple contexts may apply to the same data entity.
3. Tracking technologies such as cookies, web beacons, etc. are technologies, hence does not classify as data entity and should NOT be annotated.
4. The policy segment that you receive might be empty or not contain any information on usage of concrete personal user data - that's normal, and you should just return an empty list.

Provide the output as a list of data usage contexts with the following details for each entry:
1. The type of the context as in one of the five context types mentioned above.
2. The exact text of the context as it appears in the text segment.
3. The exact sentence of the context as it appears in the text segment.

You will be given the segment below from user input. Please identify and annotate ALL data usage contexts in the following privacy policy segment.
Your output should follow this JSON structure:

[
    {
        "action_type": "...",
        "text": "...",
    },
    {
        "action_type": "...",
        "text": "...",
    }
]
'''


SYSTEM_MESSAGE_SENTENCE_IMPROVED = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate actions in it.

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each potential data entity. DO NOT annotate sentences that do not provide specific data types or purpose types.
Examples of general phrases to omit include, but are not limited to:

"the information we collect about you"
"other data"
"any information"
"other purposes"
"purposes described in our policy"

If a sentence does not clearly indicate a specific type of personal data, DO NOT include it in your annotations.

Data usage context refers to the (core phrases within) sentences that mention the actions that are being taken with the PERSONAL DATA OF THE USER which is being mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

Note the following!
1. Multiple contexts may apply to the same data entity.
2. Tracking technologies such as cookies, web beacons, etc. are technologies, hence does not classify as data entity and should NOT be annotated.
3. The policy segment that you receive might be empty or not contain any information on usage of concrete personal user data - that's normal, and you should just return an empty list.

Provide the output as a list of data usage contexts with the following details for each entry:
1. The type of the context as in one of the five context types mentioned above. Use exact type names as specified above.
2. The exact text of the context as it appears in the text segment.

You will be given the segment below from user input. Please identify and annotate ALL data usage contexts in the following privacy policy segment.
Your output should follow this JSON structure:

[
    {
        "action_type": "...",
        "text": "...",
    },
    {
        "action_type": "...",
        "text": "...",
    }
]
'''


USER_MESSAGE_SENTENCE_TEMPLATE = '''Please annotate the following segment:

{sentence}
'''
