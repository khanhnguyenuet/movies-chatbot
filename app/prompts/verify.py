VERIFY_SYSTEM_PROMPT = """You are an assistant tasked with evaluating whether a list of movie suggestions matches a user’s preferences. You should base your evaluation on the provided input query.
"""

VERIFY_SUGGESTION_REQUEST = """
<task>
You are given a list of movie suggestions and an input query. You need to determine if they are suitable or not based on the user query.
Try analyzing the context of the request and the suggestions (find some realated information in the suggestions), then evaluate whether the suggestions match the query's criteria (e.g., genre, theme, actor preferences).
</task>

<input>
{query}
</input>

<suggestions>
{suggestions}
</suggestions>

<format>
{format_instructions}
</format>
"""