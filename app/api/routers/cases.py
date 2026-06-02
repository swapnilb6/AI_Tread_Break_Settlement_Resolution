import uuid
from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.case import IntakeResult, CaseContext
from app.schemas.common import ExceptionType, CaseStatus

router = APIRouter()


class IntakeRequest(BaseModel):
    raw_text: str
    source_system: str | None = None


@router.post("/intake", response_model=CaseContext)
def intake_case(request: IntakeRequest):
    case_id = str(uuid.uuid4())

    intake = IntakeResult(
        case_id=case_id,
        exception_type=ExceptionType.UNKNOWN,
        summary=request.raw_text[:250],
        extracted_entities={"source_system": request.source_system},
        missing_fields=[],
        confidence=0.45,
    )

    return CaseContext(
        case_id=case_id,
        status=CaseStatus.NEW,
        intake=intake,
    )