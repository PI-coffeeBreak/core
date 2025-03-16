from fastapi import FastAPI
from routes import users, activities, activity_types, messages
from dependencies.database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(activity_types.router, prefix="/activity_types", tags=["Activity Types"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])

# Run with: uvicorn main:app --reload
# load env file: --env-file <env_file>
