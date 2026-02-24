import requests
import streamlit as st


api_key_imdb = ""
api_key_tmdb = ""


def get_movie_data(imdb_id):
    url = f"http://www.omdbapi.com/?i=tt{imdb_id}&apikey={api_key_imdb}"
    response = requests.get(url)
    return response.json()

def get_tmdb_data(tmdb_id):
    # print(tmdb_id,type(tmdb_id))
    proxies = {
        'http': 'socks5h://localhost:1081',
        'https': 'socks5h://localhost:1081'
    }
    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={api_key_tmdb}"
    response = requests.get(url,proxies=proxies)
    response = response.json()
    movie_name = response['original_title']
    poster_path = f"https://image.tmdb.org/t/p/w500{response['poster_path']}"
    return movie_name,poster_path


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

    st.success("Форма отправлена!")
    # st.write(f"ID пользователя: {user_id}")
    # st.write(f"Количество рекомендаций: {num_recs}")
    # st.write(response.json())
    print(response.json())
    for id in response.json()["imdb_id"]:
        movie_name, poster_path = get_tmdb_data(id)
        st.image(poster_path,caption = movie_name)
        # print(id)
        # print(data)
        # if data['Response'] == 'True':
        #     st.subheader(data["Title"])
        #     poster_url = data["Poster"]
        #     if poster_url != "N/A":
        #         st.image(poster_url)

    # Здесь можно вызвать вашу функцию
    # recommendations = get_recommendations(user_id, num_recs)
    # st.write(recommendations)
    #
    # No connection adapters were found for 'localhost:8000/getrecs/?userId=250&recs_size=5'
