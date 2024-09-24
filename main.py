import sys
import os
from datetime import datetime

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
# print(mongo_db_url)

AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")

os.environ["AWS_ACCESS_KEY_ID"]=AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"]=AWS_SECRET_ACCESS_KEY

import pymongo

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME
from fastapi.responses import HTMLResponse
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logger.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.cloud.s3_syncer import S3Sync

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from networksecurity.utils.ml_utils.model.estimator import ModelResolver
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR
from networksecurity.constant.training_pipeline import PREDICTION_DIR
from networksecurity.constant.training_pipeline import PREDICTION_BUCKET_NAME

from networksecurity.utils.main_utils.utils import load_object

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        if train_pipeline.is_pipeline_running:
            return Response("Training pipeline is already running.")
        train_pipeline.run_pipeline()
        return Response("Training successful !!")
    except Exception as e:
            raise NetworkSecurityException(e,sys)

@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        await file.close()
        #print(df)
        model = ModelResolver(model_dir=SAVED_MODEL_DIR)
        latest_model_path = model.get_best_model_path()
        latest_model = load_object(file_path=latest_model_path)
        
        y_pred = latest_model.predict(df)
        df['predicted_column'] = y_pred
        # df['predicted_column'].replace(-1, 0)

        os.makedirs(PREDICTION_DIR,exist_ok=True)
        prediction_file_name = os.path.basename(file.filename).replace(".csv",f"_{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv")
        prediction_file_path = os.path.join(PREDICTION_DIR,prediction_file_name)
        df.to_csv(prediction_file_path,index=False,header=True)

        s3_sync = S3Sync()
        aws_url = f"s3://{PREDICTION_BUCKET_NAME}/{PREDICTION_DIR}"
        s3_sync.sync_folder_to_s3(folder = PREDICTION_DIR, aws_bucket_url = aws_url)
        
        return df.to_json()
        # table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        # return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

if __name__=="__main__":
    app_run(app, host="localhost", port=8000)