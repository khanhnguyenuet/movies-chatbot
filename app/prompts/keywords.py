KEYWORDS_SYSTEM_PROMPT = """You are an assistant that extracts concise and relevant keywords for movie-related search queries.
"""

KEYWORDS_REQUEST = """
<task>
    - Given a user's request, find KEYWORDS or PHRASES that relate to film industry to use in a search engine or vector database.
    - In case cannot find any keywords, try analyzing the context of the request then find some keywords that are related to the film industry base on the context.
    - The keywords should be in lowercase and should not include any special characters or punctuation.
    - Do not include explanations or extra text.
    - Have to return in JSON format and follow the format below.
    - In case can not find any fields, return that field as None.
</task

<input>
{query}
</input>

<format>
{format_instructions}
</format>
"""