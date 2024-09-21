SYSTEM_MESSAGE = 'You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate entities in it.'


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


USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_1_1 = '''Please annotate the given segment of privacy policy for data entities, and adhere to the following guidelines:

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

Do not output anything that is not the data entity list, such as explanations or comments.

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


USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2_1 = '''Please annotate the given sentence of the given segment of privacy policy for data entities, and adhere to the following guidelines:

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

Do not include anything that is not a data entity in your response.
Also do not output anything that is not the data entity list, such as explanations or comments.

---

Here is the privacy policy segment:

{segment}

---

Here is the sentence you should annotate:

{sentence}
'''


from .data_entity_recognition_sentence import (
    SYSTEM_MESSAGE as SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_SENTENCE,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_SENTENCE,
)


SYSTEM_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION = '''You are an annotation expert, and your task is to map phrases concerning user private data to one of the 211 categories below.
You will be given a list of categories/terms as a hierarchy, meaning that some categories will have subcategories.
You will also be given definitions of each of these categories. Please rely on these definitions.
You always have to choose the category that matches the given phrase the closest and most precise.
The categories that are "deeper" in the hierarchy are more precise, so you should use them whenever they apply, and only use the parent category, if none of the child category matches the phrase.
Here is the hierarchy of terms:

{hierarchy}

Here are definitions of these terms in form of a csv file:

{definitions}

In the following prompt, you will receive a segment (between `<segment>...</segment>`) and a list with phrases (between `<phrases>...</phrases>`, as a JSON array) within the segment, and your task is to map each one of them to the category that matches each phrase the closest and most precise.
The category must be STRICTLY of the categories in the "category" column of the attached csv file.
Return the classifications as a JSON array of entries, matching the order of the given phrases.
'''


USER_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION = '''Please classify the phrases (given later) in the following segment:

<segment>
{segment}
</segment>

The phrases to classify are:

<phrases>
{phrases}
</phrases>
'''


from .data_category_classification_gradual import (
    SYSTEM_MESSAGE_TEMPLATE as SYSTEM_MESSAGE_TEMPLATE_DATA_CATEGORY_CLASSIFICATION_GRADUAL,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_DATA_CATEGORY_CLASSIFICATION_GRADUAL,
)

from .purpose_entity_recognition_sentence import (
    SYSTEM_MESSAGE as SYSTEM_MESSAGE_PURPOSE_ENTITY_RECOGNITION_SENTENCE,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY_RECOGNITION_SENTENCE,
)

from .purpose_category_classification import (
    SYSTEM_MESSAGE_TEMPLATE as SYSTEM_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION,
    USER_MESSAGE_TEMPLATE_SENTENCE as USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION_SENTENCE,
)

from .action_recognition import (
    SYSTEM_MESSAGE as SYSTEM_MESSAGE_ACTION_RECOGNITION,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION,
    SYSTEM_MESSAGE_SENTENCE as SYSTEM_MESSAGE_ACTION_RECOGNITION_SENTENCE,
    USER_MESSAGE_SENTENCE_TEMPLATE as USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION_SENTENCE,
)

from .protection_method import (
    SYSTEM_MESSAGE as SYSTEM_MESSAGE_PROTECTION_METHOD,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_PROTECTION_METHOD,
    USER_MESSAGE_TEMPLATE_SENTENCE as USER_MESSAGE_TEMPLATE_PROTECTION_METHOD_SENTENCE,
)

from .party_recognition import (
    SYSTEM_MESSAGE as SYSTEM_MESSAGE_PARTY_RECOGNITION,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION,
    USER_MESSAGE_TEMPLATE_SENTENCE as USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION_SENTENCE,
)

from .relation_recognition import (
    SYSTEM_MESSAGE as SYSTEM_MESSAGE_RELATION_RECOGNITION,
    SYSTEM_MESSAGE_RENAMED as SYSTEM_MESSAGE_RELATION_RECOGNITION_RENAMED,
    SYSTEM_MESSAGE_RENAMED_MORE_INSTRUCT as SYSTEM_MESSAGE_RELATION_RECOGNITION_RENAMED_MORE_INSTRUCT,
    USER_MESSAGE_TEMPLATE as USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION,
)
