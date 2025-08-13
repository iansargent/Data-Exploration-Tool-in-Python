from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

def create_data_router(prefix: str, load_fn, process_fn=None):
    router = APIRouter(prefix=prefix)

    @router.get("/")
    def load_data():
        try:
            gdf = load_fn()
            if process_fn:
                gdf = process_fn(gdf)
            geojson = json.loads(gdf.to_json())
            return JSONResponse(content=geojson)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router