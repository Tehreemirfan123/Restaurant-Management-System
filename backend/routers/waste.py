from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_staff
from schemas.schemas import WasteLogCreate, WasteLogResponse
from services.waste_service import create_waste, list_waste


router = APIRouter(
    prefix="/waste",
    tags=["Waste"],
    dependencies=[Depends(get_current_staff)],
)


@router.get("", response_model=list[WasteLogResponse])
def read_waste(db: Session = Depends(get_db)):
    return list_waste(db)


@router.post(
    "",
    response_model=WasteLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_waste(data: WasteLogCreate, db: Session = Depends(get_db)):
    return create_waste(db, data)
