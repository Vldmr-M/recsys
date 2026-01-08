import sqlite3

import joblib
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix


def refit_model():
    print("\n MODEL REFIT PROCESS STARTING\n")
    global model
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    new_model = AlternatingLeastSquares(
        factors=10, regularization=0.5, alpha=10, iterations=15
    )
    res = cur.execute("SELECT * FROM ratings;")
    # csr_utils = pd.pivot_table(
    #     data=ratings, values="rating", index="userId", columns="movieId"
    # )
    new_model.fit(csr_matrix(res.fetchall()))
    model = new_model
    print("\n MODEL REFIT PROCESS ENDED SUCCESSFULLY\n")


app = FastAPI()

model = joblib.load("model.pkl")

con = sqlite3.connect("example.db")
cur = con.cursor()

res = cur.execute("SELECT * FROM movies;")

scheduler = BackgroundScheduler()
scheduler.add_job(refit_model, "interval", days=1, start_date="2026-01-01 00:00:00")
scheduler.start()

movies = pd.DataFrame(res.fetchall(), columns=["movieId", "title", "genres"])
res = cur.execute("SELECT * FROM ratings;")
ratings = pd.DataFrame(
    res.fetchall(), columns=["userId", "movieId", "rating", "timestamp"]
)

# movies = pd.read_csv("movies.csv")
# ratings = pd.read_csv("ratings.csv")

util_df = pd.pivot_table(
    data=ratings, values="rating", index="userId", columns="movieId"
)
csr_utils = csr_matrix(util_df)


# class Movie(BaseModel):
#     movieId: int
#     movieTitle: str


@app.get("/add_interaction")
async def add_interaction(userid: int, itemid: int, rating: int, timestamp=1537674946):
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    res = cur.execute(
        f"INSERT INTO ratings(userId,movieId,rating,timestamp) values({userid},{itemid},{rating},{timestamp});"
    )
    print("\ninserting data in db\n")
    print(res.fetchall())


@app.get("/getrecs")
async def recommendations(movieId: int, recs_size: int):
    if recs_size > 50:
        recs_size = 10

    ids, scores = model.recommend(
        movieId, csr_utils[movieId], recs_size, filter_already_liked_items=False
    )

    return {"ids": ids.tolist(), "scores": scores.tolist()}
