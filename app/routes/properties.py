from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from app.database import get_db
from app.dependencies import extract_email, require_role, require_role_any
from app.models.property import PropertyCreate, PropertyResponse

router = APIRouter(prefix="/properties", tags=["properties"])


def _serialize(doc: dict) -> PropertyResponse:
    return PropertyResponse(
        id=str(doc["_id"]),
        codigo_imovel=doc["codigo_imovel"],
        data_cadastro=doc["data_cadastro"],
        preco=doc["preco"],
        status=doc["status"],
        admin_email=doc["admin_email"],
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PropertyResponse)
async def create_property(
    body: PropertyCreate,
    payload: dict = Depends(require_role("ADMIN")),
):
    db = get_db()
    doc = {
        "codigo_imovel": body.codigo_imovel,
        "data_cadastro": datetime.now(timezone.utc),
        "preco": body.preco,
        "status": body.status.value,
        "admin_email": extract_email(payload),
    }
    result = await db["properties"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("", response_model=list[PropertyResponse])
async def list_properties(
    payload: dict = Depends(require_role_any("ADMIN", "USER")),
):
    db = get_db()
    cursor = db["properties"].find()
    docs = await cursor.to_list(length=None)
    return [_serialize(d) for d in docs]


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: str,
    payload: dict = Depends(require_role("ADMIN")),
):
    try:
        oid = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    db = get_db()
    result = await db["properties"].delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
