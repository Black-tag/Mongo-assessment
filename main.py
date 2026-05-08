from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, HTTPException
from models import ProjectCreate, ProjectUpdate
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId
from caching import get_cache, set_cache, init_redis
from schedule import init_scheduler, worker_loop


client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["dcforms"]


@asynccontextmanager
async def lifespan(app):
    await init_redis()
    await init_scheduler()
    await db.projects.create_index([("prj_name")], unique=False)
    yield

    


app = FastAPI(lifespan=lifespan)





# question 1


@app.post("/create")
async def create_project(project: ProjectCreate):

    existing = await db.projects.find_one({"prj_name": project.prj_name})
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Project with name '{project.prj_name}' already exists",
        )

    result = await db.projects.insert_one(project.dict())
    return {"message": "successfully added project to db", "statuscode": 201}


# question 1


@app.put("/put/{project_id}")
async def update_project(project_id: str, project: ProjectUpdate):
    data = project.dict(exclude_unset=True)
    data.pop("prj_id", None)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    existing = await db.projects.find_one({"prj_id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.projects.update_one({"prj_id": project_id}, {"$set": data})

    if result.matched_count == 0:
        return {"error": "Project not found"}

    return {"message": "updation successful"}


# question 2


@app.delete("/delete/{project_id}")
async def delete_project(project_id: str):
    project_id = project_id.strip('"')
    query = {"prj_id": project_id}

    if ObjectId.is_valid(project_id):
        query = {"_id": ObjectId(project_id)}

    project = await db.projects.find_one(query)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    prj_id = project.get("prj_id")

    await db.forms.delete_many({"projectId": prj_id})
    await db.formdata.delete_many({"projectId": prj_id})

    await db.projects.delete_one({"_id": project["_id"]})

    return {"message": "Project and related data deleted"}


# question 3


@app.get("/matched")
async def get_sorted_products():

    key = "/matched"

    cache = await get_cache(key)

    if cache:
        return {"source": "cache", "data": cache}

    pipeline = [
        {
            "$match": {
                "customer_id": 28,
                "created_on": {
                    "$gte": datetime(2020, 1, 1),
                    "$lt": datetime(2021, 1, 1),
                },
            }
        },
        {"$sort": {"created_on": -1}},
        {
            "$project": {
                "_id": 0,
                "prj_id": 1,
                "prj_name": 1,
                "customer_id": 1,
                "created_on": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$created_on"}
                },
            }
        },
    ]
    cursor = db.projects.aggregate(pipeline)
    result = await cursor.to_list(length=100)
    await set_cache(key, result, 300)
    return {"source": "db", "data": result}


@app.get("/project-forms")
async def get_project_forms():

    key = "/project-forms"
    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache}

    pipeline = [
        {"$match": {"customer_id": 28}},
        {"$sort": {"created_on": -1}},
        {"$unwind": "$forms_meta"},
        {
            "$project": {
                "_id": 0,
                "form_name": "$forms_meta.form_name",
                "form_id": {"$toString": "$forms_meta._id"},
                "form_description": "$forms_meta.form_desc",
                "created_on": {
                    "$dateToString": {
                        "format": "%d-%B-%Y",
                        "date": "$forms_meta.created_on",
                    }
                },
            }
        },
    ]
    cursor = db.projects.aggregate(pipeline)
    result = await cursor.to_list(length=100)
    await set_cache(key, result, 300)
    return {"source": "DB", "data": result}


@app.get("/list-forms")
async def get_list_of_forms():
    key = "/list-forms"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache}

    pipeline = [
        {
            "$lookup": {
                "from": "forms",
                "let": {"fid": "$formId"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$fid"}]}}}
                ],
                # "localField": "formId",
                # "foreignField": "_id",
                "as": "form",
            }
        },
        {"$unwind": {"path": "$form", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "projects",
                "let": {"pid": "$projectId"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$pid"}]}}}
                ],
                # "localField": "prj_id",
                # "foreignField": "projectId",
                "as": "project",
            }
        },
        {"$unwind": {"path": "$project", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "user",
            }
        },
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "approved_by": 1,
                "created_by": "$createdby",
                "firstname": "$user.firstname",
                "last_name": "$user.last_name",
                "form_status": 1,
                "id": {"$toString": "$_id"},
                "sent_by": "$sentby",
                "sentby_name": 1,
                "submission_type": 1,
                "submitted_date": {
                    "$dateToString": {"format": "%d %b, %Y", "date": "$submitted_time"}
                },
                "user_id": 1,
                "user_type": 1,
                "forms": {
                    "name": "$form.form_name",
                    "form_id": {"$toString": "$form._id"},
                    "projects": {
                        "name": "$project.prj_name",
                        "project_id": {"$toString": "$project._id"},
                    },
                },
            }
        },
    ]

    cursor = db.formdata.aggregate(pipeline)
    result = await cursor.to_list(length=100)
    await set_cache(key, result, 300)
    return {"source": "db", "data": result}
