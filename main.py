from fastapi import FastAPI, HTTPException
from models import ProjectCreate, ProjectUpdate
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId


app = FastAPI()

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["dcforms"]

# question 1

@app.post("/create")
async def create_project(project: ProjectCreate):
    result = await db.project.insert_one(project.dict())
    return {"message":"successfully added project to db", "statuscode": 201}


# question 1

@app.put("/put/{project_id}")
async def update_project(project_id: str, project: ProjectUpdate):
    data = project.dict(exclude_unset=True)
    data.pop("prj_id", None)

    result = await db.project.update_one(
        {"prj_id": project_id},   
        {"$set": data}            
    )

    if result.matched_count == 0:
        return {"error": "Project not found"}

    return {"message": "updation successful"}


# question 2 

@app.delete("/delete/{project_id}")
async def delete_project(project_id: str):
    try:
        obj_id = ObjectId(project_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    project = await db.project.find_one({"_id": obj_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    prj_id = project.get("prj_id")

    
    await db.forms.delete_many({"projectId": prj_id})
    await db.formdata.delete_many({"projectId": prj_id})

    await db.project.delete_one({"_id": obj_id})

    return {"message": "Project and related data deleted"}





# question 3

@app.get("/matched")
async def get_sorted_products():
    pipeline = [{"$match": {"customer_id": "28", "created_on": {"$gte": datetime(2020, 1, 1,), "$lt": datetime(2021, 1, 1)}}}, {"$sort": {"created_on": -1}}, {"$project": {"_id": 0, "prj_id":1, "prj_name": 1, "customer_id":1, "created_on": {"$dateToString": {"format": "%d-%m-%Y", "date": "$created_on"}}}}]
    cursor = db.project.aggregate(pipeline)
    result = await cursor.to_list(length=100)

    return result


#  question 4
@app.get("/project-forms")
async def get_project_forms():
    pipeline = [{"$match": {"customer_id": "28"}},{"$sort": {"submitted_time": -1}},{"$project": {"_id": 0,"form_name": "$formName","form_id": "$formId","form_description": "$form_data","created_on": {"$dateToString": {"format": "%d-%B-%Y","date": "$submitted_time"}}}}]

    cursor = db.formdata.aggregate(pipeline)
    result = await cursor.to_list(length=100)
    return result






# @app.get("/list")
# async def get_list_of_projects():
    
#     pipeline = [{"$match": { "customer_id": 28 } },{"$sort": { "submitted_time": -1 }},{ "$project": {"_id": 0, "form_name": "$formName","form_id": "$formId","form_description": "$form_data","created_on": {"$dateToString": {"format": "%d-%B-%Y","date": "$submitted_time"}}}}]
#     cursor = db.formdata.aggregate(pipeline)
#     result = await cursor.to_list(length=100)

#     return result




# question 5

@app.get("/list-forms")
async def get_list_of_forms():
    pipeline = [{ "$project": { "_id": 0, "approved_by": "$approved_by", "created_by": "$createdby", "firstname": "$createdby", "last_name": "", "form_status": "$form_status", "id": {"$toString": "$_id"}, "sent_by": "$sentby", "sentby_name": "$sentby_name", "submission_type": "Cloud", "submitted_date": { "$dateToString": { "format": "%d %b, %Y", "date": "$submitted_time" } }, "user_id": "$user_id", "user_type": "$user_type", "forms": { "name": "$formName", "form_id": "$formId", "projects": { "name": "$projectName", "project_id": "$projectId" } } } }]
    cursor = db.formdata.aggregate(pipeline)
    result = await cursor.to_list(length=100)

    return result 