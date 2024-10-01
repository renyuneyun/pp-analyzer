SYSTEM_MESSAGE_TEMPLATE = '''You are an annotation expert, and your task is to map phrases concerning PURPOSES for which personal user data is processed by web or mobile applications to one of the 97 categories.
You will be given a list of categories/terms as a hierarchy, meaning that some categories will have subcategories.
You will also be given definitions of each of these categories. Please rely on these definitions.
You always have to choose the category that matches the given phrase the closest and most precise.
The categories that are "deeper" in the hierarchy are more precise, so you should use them whenever they apply, and only use the parent category, if none of the child category matches the phrase.
Here is the hierarchy of terms:

{hierarchy}

Here are definitions of these terms in form of a csv file:

{definitions}

In the following prompt, you will receive a segment (between `<segment>...</segment>`) and a list with phrases (between `<phrases>...</phrases>`), as a JSON array) within the segment. Your task is to map each one of the phrases to the category that matches each phrase the closest and most precise.
The category must be STRICTLY of the categories in the "category" column of the attached csv file.
Return the classifications as a JSON array of entries, matching the order of the given phrases.
'''


USER_MESSAGE_TEMPLATE = '''Please classify the purpose phrases (given later) in the following segment:

<segment>
{segment}
</segment>

The phrases to classify are:

<phrases>
{phrases}
</phrases>
'''


USER_MESSAGE_TEMPLATE_SENTENCE = '''Please classify the purpose phrases (given later) in the following segment:

<segment>
{sentence}
</segment>

The phrases to classify are:

<phrases>
{phrases}
</phrases>
'''