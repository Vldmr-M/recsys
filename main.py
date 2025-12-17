import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from scipy.sparse import csr_matrix

app = FastAPI()

model = joblib.load("model.pkl")
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
movies.movieId = movies.movieId - 1
ratings.movieId = ratings.movieId - 1
ratings.userId = ratings.userId - 1
movies.index = movies.movieId
util_df = pd.pivot_table(
    data=ratings, values="rating", index="userId", columns="movieId"
)
csr_utils = csr_matrix(util_df)


class Movie(BaseModel):
    movieId: int
    movieTitle: str


@app.get("/getrecs")
async def recommendations(movieId: int, recs_size: int):
    if recs_size > 50:
        recs_size = 10

    ids, scores = model.recommend(
        movieId, csr_utils[movieId], recs_size, filter_already_liked_items=False
    )

    return {"ids": ids.tolist(), "scores": scores.tolist()}
