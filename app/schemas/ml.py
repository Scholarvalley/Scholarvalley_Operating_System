from typing import Optional

from pydantic import BaseModel


class MLConsentUpdate(BaseModel):
    applicant_id: Optional[int] = None
    consent_given: bool = True
    version: str = "v1"


class MLRecommendationRequest(BaseModel):
    applicant_id: int
    context: dict


class MLRecommendationResponse(BaseModel):
    applicant_id: int
    recommendation: str
    model_version: str

