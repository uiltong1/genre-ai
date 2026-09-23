from pydantic import BaseModel, Field
from typing import Dict


class PredictResponseSchema(BaseModel):
    filename: str = Field(..., example="musica_teste.mp3")
    predicted_genre: str = Field(..., example="rock")
    confidence: float = Field(..., example=0.9234)
    confidence_percentage: str = Field(..., example="92.34%")
    all_probabilities: Dict[str, float] = Field(
        ...,
        example={
            "rock": 0.9234,
            "pop": 0.0512,
            "metal": 0.0254
        }
    )

    class Config:
        from_attributes = True