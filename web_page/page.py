import requests
import streamlit as st
import streamlit.components.v1 as components

api_key_imdb = "2d89625d"
api_key_tmdb = "ffd0bec30eafeebf7f673cb848fb68ff"


def get_movie_data(imdb_id):
    url = f"http://www.omdbapi.com/?i=tt{imdb_id}&apikey={api_key_imdb}"
    response = requests.get(url)
    return response.json()


def get_tmdb_data(tmdb_id):
    # my own vpn
    proxies = {"http": "socks5h://localhost:1081", "https": "socks5h://localhost:1081"}

    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={api_key_tmdb}"
    response = requests.get(url, proxies=proxies)
    response = response.json()
    movie_name = response["original_title"]
    poster_path = f"https://image.tmdb.org/t/p/w500{response['poster_path']}"
    return movie_name, poster_path


st.title("Получение рекомендаций")

# Форма
with st.form("recommendation_form"):
    user_id = st.text_input("Введите ID пользователя")
    num_recs = st.number_input(
        "Количество рекомендаций", min_value=1, max_value=100, value=5, step=1
    )

    submit_button = st.form_submit_button("Отправить")

# Обработка отправки
if submit_button:
    response = requests.get(
        f"http://localhost:8000/getrecs/?userId={user_id}&recs_size={num_recs}"
    )
    images = []
    st.success("Форма отправлена!")
    for id in response.json()["imdb_id"]:
        movie_name, poster_path = get_tmdb_data(id)
        images.append({"url": poster_path, "caption": movie_name})
        # st.image(poster_path, caption=movie_name)

    cards = "".join(
        [
            f"""
        <div class="image-card">
            <img src="{item["url"]}">
            <div class="caption">{item["caption"]}</div>
        </div>
        """
            for item in images
        ]
    )

    html = f"""
    <style>
    .horizontal-scroll {{
        display: flex;
        overflow-x: auto;
        gap: 20px;
    }}

    .image-card {{
        flex-shrink: 0;
        text-align: center;
    }}

    .image-card img {{
        height: 400px;
        border-radius: 12px;
        display: block;
    }}

    .caption {{
        margin-top: 8px;
        font-size: 14px;
    }}
    </style>

    <div class="horizontal-scroll">
    {cards}
    </div>
    """

    components.html(html, height=470, scrolling=True)
