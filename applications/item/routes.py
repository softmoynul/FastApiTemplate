from fastapi import APIRouter
router = APIRouter()

@router.get("/1", tags=["Group 1"])
async def Item1():
    return {"hii! this is item."}

@router.get("/2", tags=["Group 1"])
async def Item2():
    return {"hii! this is item."}

@router.get("/3", tags=["Group 2"])
async def Item3():
    return {"hii! this is item."}

@router.get("/4", tags=["Group 2"])
async def Item4():
    return {"hii! this is item."}