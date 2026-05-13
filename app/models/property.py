from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class StatusEnum(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    VENDIDO = "VENDIDO"
    CANCELADO = "CANCELADO"


class PropertyCreate(BaseModel):
    codigo_imovel: str
    preco: float
    status: StatusEnum = StatusEnum.DISPONIVEL


class PropertyResponse(BaseModel):
    id: str
    codigo_imovel: str
    data_cadastro: datetime
    preco: float
    status: StatusEnum
    admin_email: str

    model_config = ConfigDict(from_attributes=True)
