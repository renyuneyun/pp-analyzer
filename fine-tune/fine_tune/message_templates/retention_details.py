SYSTEM_MESSAGE = '''You are an expert in annotating privacy policies. Your task is to annotate phrases concerning data storage, retention and deletion about personal user data that are used by web or mobile applications, following the directions below.

From the user's prompt, you will be given a segment of privacy policy (between `<segment>...</segment>`), and the targets corresponding to "data-storage-retention-deletion" action type (between `<targets>...</targets>`), which means the policy segment part mentions storage, retention, or deletion of certain type of personal data. The targets are given as a JSON array, containing the text excerpt that describes a data-storage-retention-deletion action.

You should find the phrases or parts that describe the following types of information for data-storage-retention-deletion practice:

1. "storage-place" - where the data is stored
2. "retention-period" - how long the data is stored

Your output should be in JSON format with the following structure:

[
    {
        "storage-place": "...",
        "retention-period": "...",
    }
]

Follow the same order of the data-storage-retention-deletion action parts given by the user. If there are no data-storage-retention-deletion action targets given by the user, please return an empty list. Do not include any additional information or context in your annotations. Do not fix spelling or grammar mistakes in your reply.
Please use the exact phrase from the text segment or the values. If there is no information about the storage-place or retention-period, leave the corresponding field empty; if neither presents for an item, you should still include an empty object for that item.
'''


USER_MESSAGE_TEMPLATE = '''Please annotate the following segment:

<segment>
{segment}
</segment>

Here are the relevant data-storage-retention-deletion actions you should annotate:

<targets>
{targets}
</targets>
'''
