from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from typing import Dict, Any

def to_object_id(id_str: str) -> ObjectId:
    """
    Converts a string ID to ObjectId, raising HTTPException if invalid.
    """
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"'{id_str}' is not a valid ObjectId")

def from_mongo(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB document (_id) to JSON-friendly format (id).
    """
    if not document:
        return document
    document = document.copy()
    document["id"] = str(document.pop("_id"))
    return document