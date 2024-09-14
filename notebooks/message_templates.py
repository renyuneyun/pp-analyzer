USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION = '''Please annotate the given segment of privacy policy for data entities, and adhere to the following guidelines:

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each potential data entity. DO NOT annotate general phrases that do not provide specific data types.
Examples of general phrases to omit include, but are not limited to:

"your personal information"
"the information you share (with us)"
"the information we collect about you"
"other data"
"information about you"
"personal information"
"user information"
"customer data"
"collected information"
"any information"

If a phrase does not clearly indicate a specific type of personal data, DO NOT include it in your annotations.

Data entities are refers to the phrases that mention PERSONAL DATA OF THE USER which is being mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

Note the following!
1. Personal user data that is mentioned outside of one of these contexts does not classify as data entity and should NOT be annotated.
2. Multiple contexts may apply to the same data entity.
3. Tracking technologies such as cookies, web beacons, etc. are technologies, hence does not classify as data entity and should NOT be annotated.
4. The data segment that you receive might be empty or not contain any information on usage of concrete personal user data - that's normal, and you should just return an empty list.

Provide the output as a list of data entities with the following details for each entity:
1. The type of the context in which this datum is mentioned.
2. The exact text of the data entity as it appears in the text segment.

Here is the privacy policy segment to annotate:

{segment}
'''

USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2 = '''Please annotate the given sentence of the given segment of privacy policy for data entities, and adhere to the following guidelines:

IMPORTANT: Filtering Out General Phrases
Before annotating, carefully check each potential data entity. DO NOT annotate general phrases that do not provide specific data types.
Examples of general phrases to omit include, but are not limited to:

"the information we collect about you"
"other data"
"any information"

If a phrase does not clearly indicate a specific type of personal data, DO NOT include it in your annotations.

Data entities are refers to the phrases that mention PERSONAL DATA OF THE USER which is being mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

Note the following!
1. Personal user data that is mentioned outside of one of these contexts does not classify as data entity and should NOT be annotated.
2. Multiple contexts may apply to the same data entity.
3. Tracking technologies such as cookies, web beacons, etc. are technologies, hence does not classify as data entity and should NOT be annotated.
4. The data segment that you receive might be empty or not contain any information on usage of concrete personal user data - that's normal, and you should just return an empty list.

Provide the output as a list of data entities with the following details for each entity:
1. The type of the context in which this datum is mentioned.
2. The exact text of the data entity as it appears in the text segment.

---

Here is the privacy policy segment:

{segment}

---

Here is the sentence you should annotate:

{sentence}
'''
