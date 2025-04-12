SEARCH_SYSTEM_PROMPT = """
You are an AI assistant capable of using the Bing Search tool to find accurate movies. Cite the source if possible.
"""

REQUEST = """Use Bing Search Service to search at least 2 movies wich sastisfy the following criteria:
<criteria>
    {condition}
</criteria>

<instruction>
    1. In case you can not find any informations, return an EMTPY list.
    2. Only return the final result, do not add any other text.
    3. Each movie's description includes: the name, the genre, and a short over view, a link (if possible).
    4. Only return in JSON format.
    5. Have to follow the following format:
    <format>
        {format_instructions}
    </format>
    6. If any field in the above format is List type but the answer contains only one item, please wrap it in a list.
</instruction>
"""

MOVIE_FORMAT_SYSTEM = """
You are a helpful assistant that formats strings according to user-specified formatting rules. Always ensure proper capitalization, punctuation, spacing, and consistent style as described in the instructions.
"""

MOVIE_FORMAT_REQUEST = """
Given an input string consist of one or multiple movies and their information. Convert it to the format denfined below.
Only return the final answer and do not add more information.
<input>
    {text}
</input>

<format>
    {instruction}
</format>
"""