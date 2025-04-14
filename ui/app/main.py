import streamlit as st
import requests
import re
import os

MOVIE_SEARCH_BASE_URL = os.getenv("ENDPOINT_BASE_URL")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def fetch_movie_poster(movie_name):
    try:
        response = requests.get(TMDB_SEARCH_URL, params={
            "api_key": TMDB_API_KEY,
            "query": movie_name
        })
        data = response.json()
        results = data.get("results", [])
        if results:
            poster_path = results[0].get("poster_path")
            if poster_path:
                return TMDB_IMAGE_BASE + poster_path
    except Exception as e:
        print(f"TMDB error: {e}")
    return None

def call_movie_api(query):
    api_url = f"{MOVIE_SEARCH_BASE_URL}/pipeline/?query={query}"
    try:
        response = requests.post(api_url, headers={"accept": "application/json"})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ API error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
    return None

def parse_response(response_text):
    movies = []
    raw_movies = response_text.strip().split("==========")

    for block in raw_movies:
        block = block.strip()
        if not block:
            continue

        movie_data = {}
        fields = re.findall(r"\s*([A-Za-z ]+):\s*(.*?)(?=,\s*\n|$)", block, re.DOTALL)
        for key, value in fields:
            clean_key = key.strip().capitalize()
            clean_value = value.strip().replace('\n', ' ')
            movie_data[clean_key] = clean_value
        movies.append(movie_data)

    return movies

def display_movies(movies):
    for movie in movies:
        with st.container():
            st.markdown("----")
            st.markdown(f"### 🎞️ {movie.get('Name', 'Unknown Title')}")

            poster_url = fetch_movie_poster(movie.get("Name", ""))
            cols = st.columns([1, 3])

            with cols[0]:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.image("https://placehold.co/300x450", use_container_width=True)

            with cols[1]:
                overview = movie.get("Overview", "No overview available.")
                st.markdown(f"<div style='text-align: justify;'><strong>📖 Overview:</strong> {overview}</div>", unsafe_allow_html=True)

                genre = movie.get("Genre", "")
                if genre:
                    st.markdown(f"**🎭 Genre:** `{genre}`")

                actors = movie.get("Actor", "")
                if actors:
                    actor_list = [a.strip() for a in actors.split(",") if a.strip()]
                    top_actors = ", ".join(actor_list[:5])
                    st.markdown(f"**👤 Main Cast:** {top_actors}...")

                extra_fields = {k: v for k, v in movie.items() if k.lower() not in ["name", "overview", "genre", "actor"]}
                if extra_fields:
                    st.markdown("**ℹ️ Additional Info:**")
                    for k, v in extra_fields.items():
                        st.markdown(f"- **{k}:** {v}")

def display_movies_v2(movies):
    for movie in movies:
        with st.container():
            st.markdown("----")
            st.markdown(f"### 🎞️ {movie.get('title', 'Unknown Title')}")

            poster_url = fetch_movie_poster(movie.get("title", ""))
            cols = st.columns([1, 3])

            with cols[0]:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.image("https://placehold.co/300x450", use_container_width=True)

            with cols[1]:
                overview = movie.get("overview", "No overview available.")
                st.markdown(
                    f"""
                    <div style='text-align: justify; font-size: 20px;'>
                        <strong>📖 Overview:</strong> {overview}
                    </div>
                    <br>
                    """,
                    unsafe_allow_html=True
                )

                genre = movie.get("genre", "")
                if genre:
                    st.markdown(f"**🎭 Genre:** `{genre}`")

                actors = movie.get("actor", "")
                if actors:
                    actor_list = [a.strip() for a in actors.split(",") if a.strip()]
                    top_actors = ", ".join(actor_list[:5])
                    st.markdown(f"**👤 Main Cast:** {top_actors}...")

                rating = movie.get("rating", "")
                if rating:
                    st.markdown(f"**⭐ Rating:** {rating}")

                release_date = movie.get("release_date", "")
                if release_date:
                    st.markdown(f"**📅 Release Date:** {release_date}")

                language = movie.get("language", "")
                if language:
                    st.markdown(f"**🗣️ Language:** {language}")

                country = movie.get("contry", "")
                if country:
                    st.markdown(f"**🏴󠁥󠁳󠁰󠁶󠁿 Country:** {country}")

# Streamlit app UI
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎥",
    layout="wide"
)
# Sidebar input
st.sidebar.title("🎯 Movie Preferences")
st.sidebar.markdown("Describe the kind of movie you’re looking for:")
query = st.sidebar.text_area("📝 Description", height=120, placeholder="e.g. find for me some action films in 2024")

st.title("🎬 Movie Recommender Based on Chat Description")
st.markdown("🤖 We analyze your input and recommend the best matching movies!")

if st.sidebar.button("🔍 Find Movies"):
    if query.strip():
        with st.spinner("Calling movie recommendation API..."):
            result = call_movie_api(query.strip())
            # result_text = result["suggestion"]
            result_list = result["response"]

        # if result_text:
        #     movies = parse_response(result_text)
        #     if movies:
        #         st.success(f"🎉 Found {len(movies)} movie(s):")
        #         display_movies(movies)
        #     else:
        #         st.warning("No matching movies found.")
        # else:
        #     st.error("No response from the recommendation API.")

        if result_list:
            st.success(f"🎉 Found {len(result_list)} movie(s):")
            display_movies_v2(result_list)
        else:
            st.error("No response from the recommendation API.")
    else:
        st.warning("Please enter a description.")
