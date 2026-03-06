FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install scikit-surprise fastapi catboost APScheduler
CMD [ "fasapi", "dev", "main.py"]
