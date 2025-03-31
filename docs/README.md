# Plugin Development Guide

This guide explains how to create plugins for the CoffeeBreak Core application. Plugins allow you to extend the application's functionality dynamically.

## Plugin Structure

A plugin is a Python package located inside the `plugins/` directory. The package must include an `__init__.py` file to define the plugin's properties and functionality.

### Required Structure

```
plugins/
└── my_plugin/
    ├── __init__.py
    └── endpoints.py
```

### Mandatory Properties

The `__init__.py` file must define the following mandatory properties:

- **`REGISTER`**: A callable function that initializes and registers the plugin.
- **`router`**: A FastAPI router of type `utils.api.Router` for registering API endpoints.

### Optional Properties

Plugins can also define the following optional properties:

- **`UNREGISTER`**: A callable function to clean up and unregister the plugin.
- **`DESCRIPTION`**: A string describing the plugin's functionality.
- **`DEPENDENCIES`**: A list of other plugins or modules required by this plugin.

## Example Plugin

Below is an example of a simple plugin:

### Directory Structure

```
plugins/
└── example_plugin/
    ├── __init__.py
```

### `__init__.py`

```python
# filepath: plugins/example_plugin/__init__.py
from utils.api import Router, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dependencies.database import Base, get_db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional

# Define the database model
class MyModel(Base):
    __tablename__ = 'my_model'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id'))
    attribute1 = Column(Integer, default=1)
    
    activity = relationship("Activity", backref="my_models")

# Define the Pydantic schema
class MyModelSchema(BaseModel):
    id: Optional[int]
    activity_id: int
    attribute1: Optional[int] = 1

    class Config:
        from_attributes = True

# Create the router
router = Router()

# CRUD endpoints
@router.post("/model")
def create_model(data: MyModelSchema, db=Depends(get_db)):
    new_model = MyModel(**data.dict(exclude_unset=True))
    try:
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred while creating the model.")
    return new_model

@router.get("/model")
def get_models(db=Depends(get_db)):
    return [MyModelSchema.model_validate(model) for model in db.query(MyModel).all()]

@router.put("/model/{model_id}", response_model=MyModelSchema)
def update_model(model_id: int, data: MyModelSchema, db=Depends(get_db)):
    model = db.query(MyModel).filter(MyModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(model, key, value)
        db.commit()
        db.refresh(model)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred while updating the model.")
    return model

@router.delete("/model/{model_id}")
def delete_model(model_id: int, db=Depends(get_db)):
    model = db.query(MyModel).filter(MyModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        db.delete(model)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred while deleting the model.")
    return {"message": "Model deleted successfully"}

@router.get("/activity/{activity_id}/models", response_model=List[MyModelSchema])
def get_models_by_activity(activity_id: int, db=Depends(get_db)):
    models = db.query(MyModel).filter(MyModel.activity_id == activity_id).all()
    if not models:
        raise HTTPException(status_code=404, detail="No models found for the given activity.")
    return models

# Plugin registration functions
def register_plugin():
    pass

def unregister_plugin():
    pass

REGISTER = register_plugin
UNREGISTER = unregister_plugin
DESCRIPTION = "An example plugin demonstrating CRUD operations with models."
```

## Registering Endpoints

To register API endpoints, create a `Router` instance in your plugin and define your routes. Ensure the router is accessible as `router` in the `__init__.py` file.

## Declaring Models

Plugins can define their own database models if needed. These models should inherit from the application's `Base` class provided by SQLAlchemy. Ensure that the models are properly registered and migrated when the application initializes.

To create a relationship with an existent model, like `Activity`, you should use the `backref` property, so that an implicit reference is created on `Activity` objects.

## Loading Plugins

The application dynamically loads plugins based on the `REGISTER` property. Ensure this is set to a callable function for your plugin to be included.

## Best Practices

- Use unique names for your plugins to avoid conflicts.
- Document your plugin's functionality and dependencies.
- Follow the application's coding standards for consistency.

For more details, refer to the main [README](../README.md).
