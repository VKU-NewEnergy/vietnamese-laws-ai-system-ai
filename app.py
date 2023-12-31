"""
Copyright (c) VKU.NewEnergy.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.data_ingestor import DataIngestor
from schemas import BatchTrainingRequest, ChatRequest, SearchRequest, TrainingRequest
from routes.chat import chat as ChatAgent
from llm.base_model.langchain_openai import LangchainOpenAI
import logging
from langchain.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
)
from core.constants import IngestDataConstants
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="Vietnamese Laws Exploration", version="1.0.0")

# Set up CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

@app.get("/health")
async def pong():
    return {"ping": "pong!"}


@app.post("/train-data")
async def train_data(request: TrainingRequest):
    charter = request.charter
    data_ingestor = DataIngestor()
    data_ingestor.load_charter(charter)


@app.post("/train-data-batch")
async def train_data(request: BatchTrainingRequest):
    list_of_charter = request.charter_list
    for charter in list_of_charter:
        new_request = TrainingRequest(charter=charter)
        await train_data(request=new_request)


@app.post("/chat")
async def chat(request: ChatRequest):
    response = await ChatAgent(request)
    return response


@app.post("/search")
async def search(request: SearchRequest):
    keyword = request.keyword
    _, retriever = LangchainOpenAI.get_langchain_retriever(vectorstore_folder_path=IngestDataConstants.VECTORSTORE_FOLDER)
    result = await retriever._aget_relevant_documents(query=keyword, run_manager = AsyncCallbackManagerForRetrieverRun.get_noop_manager())
    return result