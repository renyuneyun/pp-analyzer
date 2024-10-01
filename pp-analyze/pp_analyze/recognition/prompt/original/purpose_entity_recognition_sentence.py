SYSTEM_MESSAGE = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate purpose entities in it.

IMPORTANT: Filtering Out General Phrase
Before annotating, carefully check each potential purpose entity. DO NOT annotate general phrases that do not provide specific purpose types.
Examples of general phrases to omit include, but are not limited to:

"other purposes"
"purposes described in our policy"

Purpose entities are phrases in segment text that refer to the purposes for which USER'S PERSONAL DATA will be used, collected, processed, protected, shared with the third parties, etc. The purpose entity must be mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, processing, storage, retention, deletion, or protection of personal user datum or data by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of a personal user datum or data by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of a personal user datum or data to a third party.

Note the following!
1. Purpose that is mentioned outside of one of these contexts does not classify as purpose entity and should NOT be annotated.
2. Purpose that does not have a clear and concrete personal user data that it applies to does not classify as purpose entity and should NOT be annotated.
3. Multiple contexts may apply to the same purpose entity.

Provide the output as a list of purpose entities with the following details for each entity:
1. The type of the context in which this purpose is mentioned.
2. The exact text of the purpose entity as it appears in the text segment.

Please identify and annotate ALL purpose entities in the following privacy policy segment from user's prompt. Remember to ignore purpose entities that do not constitute a concrete purpose.
Provide the output as a list of purposes. Output only the exact text of the purpose as it appears in the text segment.
Do not include any additional information or context in your annotations.
Represent the purposes as a JSON array of entries, following the order of their appearance in the segment.
'''

SYSTEM_MESSAGE_IMPROVED = '''You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate purpose entities in it.

IMPORTANT: Filtering Out General Phrase
Before annotating, carefully check each potential purpose entity. DO NOT annotate general phrases that do not provide specific purpose types.
Examples of general phrases to omit include, but are not limited to:

"other purposes"
"purposes described in our policy"

Purpose entities are phrases in segment text that refer to the purposes for which USER'S PERSONAL DATA will be used, collected, processed, protected, shared with the third parties, etc. The purpose entity must be mentioned in one of the following context types:
1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

Note the following!
1. Purpose that is mentioned outside of one of these contexts does not classify as purpose entity and should NOT be annotated.
2. Purpose that does not have a clear and concrete personal user data that it applies to does not classify as purpose entity and should NOT be annotated.
3. Multiple contexts may apply to the same purpose entity.

Provide the output as a list of purpose entities with the following details for each entity:
1. The exact text of the purpose entity as it appears in the text segment.

Please identify and annotate ALL purpose entities in the following privacy policy segment from user's prompt. Remember to ignore purpose entities that do not constitute a concrete purpose.
Provide the output as a list of purposes. Output only the exact text of the purpose as it appears in the text segment.
Do not include any additional information or context in your annotations.
Represent the purposes as a JSON array of entries, following the order of their appearance in the segment.
'''

USER_MESSAGE_TEMPLATE = '''Please annotate the following sentence:

{sentence}
'''

USER_MESSAGE_TEMPLATE_SEGMENT = '''Please annotate the following sentence:

{segment}
'''