import sqlite3

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from catboost import CatBoost
from fastapi import FastAPI
from sklearn.preprocessing import LabelEncoder
from surprise import SVD, Dataset, Reader
from surprise.dump import load


def refit_model():
    global model
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM ratings;")

    reader = Reader(rating_scale=(1, 5))
    rating_surprise = Dataset.load_from_df(
        pd.DataFrame(res.fetchall())[["userId", "movieId", "rating"]], reader
    )
    trainset = rating_surprise.build_full_trainset()

    new_model = SVD()
    new_model.fit(trainset)
    model = new_model
    print("\n MODEL REFIT PROCESS ENDED SUCCESSFULLY\n")


app = FastAPI()


@app.get("/getrecs")
async def recommendations(userId: int, recs_size: int):
    if recs_size > 50:
        recs_size = 10
    best_items = []
    for item in all_items:
        pred = cand_model.predict(userId, item, None)
        best_items.append((pred.iid, pred.est))
    best_items = sorted(best_items, key=lambda x: x[1], reverse=True)[:200]
    most_pop_tag_dict = dict(zip(most_pop_tag["movieId"], most_pop_tag["tag"]))

    my_tags = [
        most_pop_tag_dict[i[0]] if i[0] in most_pop_tag_dict else "unknown"
        for i in best_items
    ]
    del most_pop_tag_dict
    svd_preds = pd.DataFrame(
        {
            "userId": userId,
            "movieId": [_[0] for _ in best_items],
            "svd_score": [_[1] for _ in best_items],
            "tag": my_tags,
        }
    )
    svd_preds = svd_preds.explode(["svd_score", "tag"])
    svd_preds.fillna("unknown", inplace=True)
    svd_preds["final_rating"] = rank_model.predict(svd_preds)
    svd_preds.sort_values("final_rating")
    final_preds = [
        row["movieId"] for index, row in svd_preds.head(recs_size).iterrows()
    ]
    imdb_id = [links[i] for i in final_preds]
    return {"ids": final_preds, "imdb_id": imdb_id}


@app.get("/add_interaction")
async def add_interaction(userid: int, itemid: int, rating: int, timestamp=1537674946):
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    res = cur.execute(
        f"INSERT INTO ratings(userId,movieId,rating,timestamp) values({userid},{itemid},{rating},{timestamp});"
    )
    print(res.fetchall())


scheduler = BackgroundScheduler()
scheduler.add_job(refit_model, "interval", days=1, start_date="2026-01-01 00:00:00")
scheduler.start()

cand_model = load("models/cand_model_30")[1]
rank_model = CatBoost()
rank_model.load_model("models/ranker_model.cbm")

# con = sqlite3.connect("example.db")
# cur = con.cursor()

ratings = pd.read_csv("data/ratings.csv")
user_encoder, item_encoder = LabelEncoder(), LabelEncoder()
ratings["userId"] = user_encoder.fit_transform(ratings["userId"])
ratings["movieId"] = item_encoder.fit_transform(ratings["movieId"])

tags = pd.read_csv("data/tags.csv")
tags = tags.groupby(["movieId", "tag"]).size().reset_index(name="count")
most_pop_tag = tags.loc[tags.groupby("movieId")["count"].idxmax()]
ratings = ratings.merge(most_pop_tag[["movieId", "tag"]], on="movieId", how="left")
del tags

links = pd.read_csv("data/links.csv")
links = {i.movieId: i.tmdbId for i in links.itertuples()}
all_items = ratings["movieId"].unique()
