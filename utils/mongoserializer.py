from bson import ObjectId
from typing import Any, Dict
from fastapi import HTTPException


def to_object_id(id_str: str) -> ObjectId:
    """
    Converts a string ID to ObjectId, raising HTTPException if invalid.
    """
    try:
        return ObjectId(id_str)
    except Exception:
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