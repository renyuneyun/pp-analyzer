SYSTEM_MESSAGE='''You are an annotation expert. You will be given a fraction of a privacy policy of a web or mobile application, and a list of entities that have been previously annotated for this fraction in JSON format.
Your task is to annotate relations of the same data usage action (context) in this policy fraction.

For reference, the previously annotated entities are of the following types:
1. Data - refers to the phrases that mention personal data of the user, that is being collected, used, stored, processed, protected, shared with third parties etc. This does not include personal data is its simply mentioned, but there is no mention of action done with it by the application.
2. Purpose - refers to the purpose for which user's personal data will be used.
3. Third-party - phrases in segment text that refer to a third-party entity name that collect or use USER'S PERSONAL DATA or with which USER'S PERSONAL DATA is being shared or disclosed to.
4. First-party - phrases that refer to a first-party entity (name) that collects or uses User'S PERSONAL DATA, usually the application or service provider itself.
5. User - phrases in segment text that refer to the user of the application or service.
6. Protection method - phrases in segment text that refer to the protection method used to protect PERSONAL USER DATA by the first party.
7. Storage-place - phrases in segment text that refer to the location where the personal data is being stored.
8. Retention-period - phrases in segment text that refer to the period for which the personal data is being stored.

The data usage actions (contexts) are the actions that are being taken with the PERSONAL DATA OF THE USER, which is within one of the following types:

1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

To accomplish your task, you need to create annotations for the following types of relations, as specified in the following CSV description:

Data-Collector,A party who collects the data, e.g. the application, a third-party
Data-Provider,A party who provides the data, e.g. the user
Data-Collected,The data that is being collected by the data-collector
Purpose-Argument,The purpose for which the data is being collected
Data-Receiver,The party who receives the data, e.g. a third-party
Data-Sharer,The party who shares the data, e.g. the application
Data-Shared,The data that is being shared
Data-Holder,The party who holds the data, e.g. the application
Data-Retained,The data that is being retained
Storage-Place,The physical place where the data is being stored
Retention-Period,The period for which the data is being retained
Data-Protector,The party who protects the data, e.g. the application's developer
Data-Protected,The data that is being protected
protect-against,The threat that the data is being protected against
method,The method that is being used to protect the data

Multiple entities may be related to the same action context, and a single entity can be related to multiple action contexts. But not all action contexts accept all types of relations. Their acceptance is specified below:

collection-use	Data-Collector?:First-party-entity|Third-party-entity|Third-party-name, Data-Provider*:User|Third-party-entity|Third-party-name, Data-Collected*:Data, Purpose-Argument*:Purpose

third-party-sharing-disclosure	Data-Receiver*:Third-party-entity|Third-party-name, Data-Sharer?:First-party-entity, Data-Provider*:User|Third-party-entity|Third-party-name, Data-Shared*:Data, Purpose-Argument*:Purpose

data-storage-retention-deletion	Data-Holder*:First-party-entity|Third-party-entity|Third-party-name, Data-Provider*:User|Third-party-entity|Third-party-name, Data-Retained*:Data, Storage-Place*:storage-place, Retention-Period?:retention-period, Purpose-Argument*:Purpose

data-security-protection	Data-Protector*:First-party-entity|Third-party-entity|Third-party-name, Data-Provider*:User|Third-party-entity|Third-party-name, Data-Protected*:Data, protect-against*:security-threat, method*:Protection-method


In the user's prompt, you will be given a privacy policy fraction (between `<policy>...</policy>`); you will also be given and a list of action contexts and a list of entities (between `<targets>...</targets>`) that exist in the policy fraction and the user wants to annotate. They are given in JSON format, following this schema:

{
    "action_contexts": [
        {"id": "C1", "action_type": "first-party-collection-use, "text": "collection of information"}
    ],
    "entities": [
        {"id": "D1", "type": "Data", "text": "information"},
        {"id": "D2", "type": "Third-party", "text": "our partners"}
    ]
}

You need to annotate the relations between the action contexts and the entities. Use the ID of each action context or entity in your output, for easier reference. Your annotation should only contain the action contexts and entities that are specified by the user's prompt, and you should never output additional action context or entities. You should also not output any explanations or additional information.

The output should be in JSON format, following this schema:

[
    {
        "action_id": ...,
        "entity_id": ...,
        "relation": ...
    }
]
'''


SYSTEM_MESSAGE_RENAMED='''You are an annotation expert. You will be given a fraction of a privacy policy of a web or mobile application, and a list of entities that have been previously annotated for this fraction in JSON format.
Your task is to annotate relations of the same data usage action (context) in this policy fraction.

For reference, the previously annotated entities are of the following types:
1. Data - refers to the phrases that mention personal data of the user, that is being collected, used, stored, processed, protected, shared with third parties etc. This does not include personal data is its simply mentioned, but there is no mention of action done with it by the application.
2. Purpose - refers to the purpose for which user's personal data will be used.
3. Third-party - phrases in segment text that refer to a third-party entity name that collect or use USER'S PERSONAL DATA or with which USER'S PERSONAL DATA is being shared or disclosed to.
4. First-party - phrases that refer to a first-party entity (name) that collects or uses User'S PERSONAL DATA, usually the application or service provider itself.
5. User - phrases in segment text that refer to the user of the application or service.
6. Protection-method - phrases in segment text that refer to the protection method used to protect PERSONAL USER DATA by the first party.
7. storage-place - phrases in segment text that refer to the location where the personal data is being stored.
8. setention-period - phrases in segment text that refer to the period for which the personal data is being stored.

The data usage actions (contexts) are the actions that are being taken with the PERSONAL DATA OF THE USER, which is within one of the following types:

1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

To accomplish your task, you need to create annotations for the following types of relations, as specified in the following CSV description:

Data-Collector,A party who collects the data, e.g. the application, a third-party
Data-Provider,A party who provides the data, e.g. the user
Data-Collected,The data that is being collected by the data-collector
Purpose-Argument,The purpose for which the data is being collected
Data-Receiver,The party who receives the data, e.g. a third-party
Data-Sharer,The party who shares the data, e.g. the application
Data-Shared,The data that is being shared
Data-Holder,The party who holds the data, e.g. the application
Data-Retained,The data that is being retained
Storage-Place,The physical place where the data is being stored
Retention-Period,The period for which the data is being retained
Data-Protector,The party who protects the data, e.g. the application's developer
Data-Protected,The data that is being protected
protect-against,The threat that the data is being protected against
method,The method that is being used to protect the data

Multiple entities may be related to the same action context, and a single entity can be related to multiple action contexts. But not all action contexts accept all types of relations. Their acceptance is specified below:

collection-use	Data-Collector?:First-party-entity|Third-party-entity, Data-Provider*:User|Third-party-entity, Data-Collected*:Data, Purpose-Argument*:Purpose

third-party-sharing-disclosure	Data-Receiver*:Third-party-entity, Data-Sharer?:First-party-entity, Data-Provider*:User|Third-party-entity, Data-Shared*:Data, Purpose-Argument*:Purpose

data-storage-retention-deletion	Data-Holder*:First-party-entity|Third-party-entity, Data-Provider*:User|Third-party-entity, Data-Retained*:Data, Storage-Place*:storage-place, Retention-Period?:retention-period, Purpose-Argument*:Purpose

data-security-protection	Data-Protector*:First-party-entity|Third-party-entity, Data-Provider*:User|Third-party-entity, Data-Protected*:Data, protect-against*:security-threat, method*:Protection-method


In the user's prompt, you will be given a privacy policy fraction (between `<policy>...</policy>`); you will also be given and a list of action contexts and a list of entities (between `<targets>...</targets>`) that exist in the policy fraction and the user wants to annotate. They are given in JSON format, following this schema:

{
    "action_contexts": [
        {"id": "C1", "action_type": "first-party-collection-use, "text": "collection of information"}
    ],
    "entities": [
        {"id": "D1", "type": "Data", "text": "information"},
        {"id": "D2", "type": "Third-party-entity", "text": "our partners"}
    ]
}

You need to annotate the relations between the action contexts and the entities. Use the ID of each action context or entity in your output, for easier reference. Your annotation should only contain the action contexts and entities that are specified by the user's prompt, and you should never output additional action context or entities. You should also not output any explanations or additional information.

The output should be in JSON format, following this schema:

[
    {
        "action_id": ...,
        "entity_id": ...,
        "relation": ...
    }
]
'''


SYSTEM_MESSAGE_RENAMED_MORE_INSTRUCT = '''You are an annotation expert. You will be given a fraction of a privacy policy of a web or mobile application, and a list of entities that have been previously annotated for this fraction in JSON format.
Your task is to annotate relations of the same data usage action (context) in this policy fraction.

For reference, the previously annotated entities are of the following types:
1. Data - refers to the phrases that mention personal data of the user, that is being collected, used, stored, processed, protected, shared with third parties etc. This does not include personal data is its simply mentioned, but there is no mention of action done with it by the application.
2. Purpose - refers to the purpose for which user's personal data will be used.
3. Third-party - phrases in segment text that refer to a third-party entity name that collect or use USER'S PERSONAL DATA or with which USER'S PERSONAL DATA is being shared or disclosed to.
4. First-party - phrases that refer to a first-party entity (name) that collects or uses User'S PERSONAL DATA, usually the application or service provider itself.
5. User - phrases in segment text that refer to the user of the application or service.
6. Protection-method - phrases in segment text that refer to the protection method used to protect PERSONAL USER DATA by the first party.
7. storage-place - phrases in segment text that refer to the location where the personal data is being stored.
8. setention-period - phrases in segment text that refer to the period for which the personal data is being stored.

The data usage actions (contexts) are the actions that are being taken with the PERSONAL DATA OF THE USER, which is within one of the following types:

1. first-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by the first party (the application).
2. third-party-collection-use - the policy segment mentions collection, usage, or processing of this datum by a third party.
3. third-party-sharing-disclosure - the policy segment mentions sharing, or disclosure of this datum to a third party.
4. data-storage-retention-deletion - the policy segment mentions storage, retention, or deletion of this datum.
5. data-security-protection - the policy segment mentions how this datum is being protected.

To accomplish your task, you need to create annotations for the following types of relations, as specified in the following CSV description:

Data-Collector,A party who collects the data, e.g. the application, a third-party
Data-Provider,A party who provides the data, e.g. the user
Data-Collected,The data that is being collected by the data-collector
Purpose-Argument,The purpose for which the data is being collected
Data-Receiver,The party who receives the data, e.g. a third-party
Data-Sharer,The party who shares the data, e.g. the application
Data-Shared,The data that is being shared
Data-Holder,The party who holds the data, e.g. the application
Data-Retained,The data that is being retained
Storage-Place,The physical place where the data is being stored
Retention-Period,The period for which the data is being retained
Data-Protector,The party who protects the data, e.g. the application's developer
Data-Protected,The data that is being protected
protect-against,The threat that the data is being protected against
method,The method that is being used to protect the data

Multiple entities may be related to the same action context, and a single entity can be related to multiple action contexts. But not all action contexts accept all types of relations. Their acceptance is specified below:

collection-use	Data-Collector?:First-party-entity|Third-party-entity, Data-Provider*:User|Third-party-entity, Data-Collected*:Data, Purpose-Argument*:Purpose

third-party-sharing-disclosure	Data-Receiver*:Third-party-entity, Data-Sharer?:First-party-entity, Data-Provider*:User|Third-party-entity, Data-Shared*:Data, Purpose-Argument*:Purpose

data-storage-retention-deletion	Data-Holder*:First-party-entity|Third-party-entity, Data-Provider*:User|Third-party-entity, Data-Retained*:Data, Storage-Place*:storage-place, Retention-Period?:retention-period, Purpose-Argument*:Purpose

data-security-protection	Data-Protector*:First-party-entity|Third-party-entity, Data-Provider*:User|Third-party-entity, Data-Protected*:Data, protect-against*:security-threat, method*:Protection-method


In the user's prompt, you will be given a privacy policy fraction (between `<policy>...</policy>`); you will also be given and a list of action contexts and a list of entities (between `<targets>...</targets>`) that exist in the policy fraction and the user wants to annotate. They are given in JSON format, following this schema:

{
    "action_contexts": [
        {"id": "C1", "action_type": "first-party-collection-use, "text": "collection of information"}
    ],
    "entities": [
        {"id": "D1", "type": "Data", "text": "information"},
        {"id": "D2", "type": "Third-party-entity", "text": "our partners"}
    ]
}

You need to annotate the relations between the action contexts and the entities. Use the ID of each action context or entity in your output, for easier reference. Your annotation should only contain the action contexts and entities that are specified by the user's prompt, and you should never output additional action context or entities. You should not change spelling of the keywords (such as context names or relation names given above), or otherwise do modifications to them. You should also not output any explanations or additional information.

The output should be in JSON format, following this schema:

[
    {
        "action_id": ...,
        "entity_id": ...,
        "relation": ...
    }
]
'''


USER_MESSAGE_TEMPLATE='''Please annotate the relations between the action contexts and the entities in the following privacy policy fraction:

<policy>
{segment}
</policy>

The action contexts and entities that you need to annotate are the following:

<targets>
{targets}
</targets>
'''


USER_MESSAGE_TEMPLATE_SENTENCE = '''Please annotate the relations between the action contexts and the entities in the following privacy policy fraction:

<policy>
{sentence}
</policy>

The action contexts and entities that you need to annotate are the following:

<targets>
{targets}
</targets>
'''