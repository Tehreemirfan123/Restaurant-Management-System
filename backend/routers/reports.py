from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import require_admin
from schemas.schemas import DishCosting, ReportsSummary
from services.reports_service import get_costing, get_summary


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(require_admin)],
)


@router.get("/summary", response_model=ReportsSummary)
def read_summary(
    period: str = Query("all", pattern="^(today|week|month|all)$"),
    db: Session = Depends(get_db),
):
    return get_summary(db, period)


@router.get("/costing", response_model=list[DishCosting])
def read_costing(db: Session = Depends(get_db)):
    return get_costing(db)
