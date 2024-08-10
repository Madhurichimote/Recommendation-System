import streamlit as st
import pickle
import requests
from requests.exceptions import RequestException

# Function to fetch the movie details including poster and overview using TMDb API
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=cc0d4ecc5ae922158aee90a0c4680086&language=en-US"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        return data
    except RequestException as e:
        return None

# Function to recommend Hollywood movies
def recommend_hollywood(movie):
    index = hollywood_movies[hollywood_movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(hollywood_similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []

    for i in distances[1:8]:
        movie_id = hollywood_movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)
        if movie_details:
            recommended_movies.append({
                'id': movie_id,
                'title': movie_details.get('title'),
                'poster_path': movie_details.get('poster_path'),
                'overview': movie_details.get('overview')
            })

    return recommended_movies

# Load the precomputed data for Hollywood
hollywood_movies = pickle.load(open('movies.pkl', 'rb'))
hollywood_similarity = pickle.load(open('similarity.pkl', 'rb'))


# Main UI of the web application
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# Custom CSS for background and text color
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: white;
    }

    .stTextInput label, .stSelectbox label {
        color: white;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h4 {
        color: #FF6347;
    }

    .stButton button {
        background-color: black;
        color: white;
        border: 2px solid red;
        border-radius: 5px;
        padding: 10px 20px;
    }

    .stButton button:hover {
        background-color: #FF6347;
        border-color: #FF6347;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Bollywood Recommendation", "Hollywood Recommendation"])

# Home page content
if page == "Home":
    st.markdown("<h1 style='text-align: center;'>Welcome to the Movie Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Please select a section from the sidebar to get started.</h2>", unsafe_allow_html=True)


# Hollywood recommendation content
elif page == "Hollywood Recommendation":
    st.markdown("<h1 style='text-align: center;'>Hollywood Recommendation</h1>", unsafe_allow_html=True)

    # Initialize session state for preview buttons
    if 'preview_buttons' not in st.session_state:
        st.session_state.preview_buttons = [False] * 7

    hollywood_movie_list = hollywood_movies['title'].values
    selected_hollywood_movie = st.selectbox("Select or Type a Hollywood Movie ", hollywood_movie_list)

    if st.button('Show Hollywood Recommendation'):
        recommended_movies = recommend_hollywood(selected_hollywood_movie)
        
        # Store the recommended movies in session state to keep the list persistent
        st.session_state.recommended_movies = recommended_movies
    else:
        # Load the recommended movies from session state if available
        recommended_movies = st.session_state.get('recommended_movies', [])

    # Display recommended movies
    st.markdown("<h2 style='text-align: center;'>Recommended Hollywood Movies:</h2>", unsafe_allow_html=True)

    for idx, movie in enumerate(recommended_movies, start=1):
        
        st.markdown(f"<h4 style='color: white;'>{idx}. {movie['title']}</h4>", unsafe_allow_html=True)
        
        # Display movie poster and preview button
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.image(f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}")
        
        with col2:
            if st.button(f'Preview ', key=idx):
                st.session_state.preview_buttons[idx - 1] = not st.session_state.preview_buttons[idx - 1]
            
            if st.session_state.preview_buttons[idx - 1]:
                st.markdown(f"**Overview:** {movie['overview']}")
                # Display "Explore More" button with dynamic link
                movie_link = f"https://www.themoviedb.org/movie/{movie['id']}"  # Use 'id' key here
                st.markdown(
                f"<a href='{movie_link}' target='_blank' style='text-decoration: none;'>"
                f"<button style='background-color: black; color: white; border: 2px solid red; border-radius: 5px; padding: 10px 20px;'>Explore More...</button>"
                f"</a>",
                unsafe_allow_html=True
                )

        st.markdown("---")
