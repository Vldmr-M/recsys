import requests
import streamlit as st

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
    st.write(f"ID пользователя: {user_id}")
    st.write(f"Количество рекомендаций: {num_recs}")
    st.write(response.json())

    # Здесь можно вызвать вашу функцию
    # recommendations = get_recommendations(user_id, num_recs)
    # st.write(recommendations)
    #
    # No connection adapters were found for 'localhost:8000/getrecs/?userId=250&recs_size=5'
