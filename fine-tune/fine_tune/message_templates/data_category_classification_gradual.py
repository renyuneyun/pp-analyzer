SYSTEM_MESSAGE_TEMPLATE = '''You are an annotation expert, and your task is to map phrases concerning user private data to one of the high-level categories below.
You will be given a list of categories/terms, belong to the same level of a category hierarchy. You will also be given definitions of each of these categories. Please rely on these definitions.
The category list is between `<category>...</category>`, and each row describes one category: the first element the first element is the category name, and the second element is the category description; they are separated using a comma (`,`); everything after the first comma is part of the description of the corresponding category.
You always have to choose the category that matches the given phrase the closest and most precise.
Here is the categories:

<category>
{categories}
</category>

In the following prompt, you will receive a segment (between `<segment>...</segment>`) and a list with phrases (between `<phrases>...</phrases>`), as a JSON array) within the segment. Your task is to map each one of the phrases to the category that matches each phrase the closest and most precise.
The category must be STRICTLY of the categories in the "category" column of the attached csv file.
Return the classifications as a JSON array of entries, matching the order of the given phrases.
'''


USER_MESSAGE_TEMPLATE = '''Please classify the phrases (given later) in the following segment:

<segment>
{segment}
</segment>

The phrases to classify are:

<phrases>
{phrases}
</phrases>
'''