from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import geopandas as gpd
import pyogrio

from app_utils.zoning import zoning_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(zoning_router, prefix="/load")