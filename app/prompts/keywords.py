KEYWORDS_SYSTEM_PROMPT = """
You are an assistant that extracts concise and relevant keywords for movie-related search queries.
"""

KEYWORDS_REQUEST = """
<task>
Given a user's request, return a list of at least 3 keywords or phrases that relate to film industry to use in a search engine or vector database.
In case cannot find any keywords, try analyzing the context of the request then give some keywords that are related to the film industry base on the context.
Only return the keywords as a JSON array of strings. Do not include explanations or extra text.
</task>

<examples>
User: "Can you recommend a psychological thriller like Shutter Island?"
Keywords: ["psychological thriller", "Shutter Island"]

User: "Looking for feel-good animated movies with animal characters"
Keywords: ["feel-good", "animated", "animal characters"]

User: "Find documentaries about filmmaking or famous directors"
Keywords: ["documentaries", "filmmaking", "famous directors"]
</examples>

<input>
{query}
</input>

<format>
{format_instructions}
</format>
"""