from pydantic import BaseModel, ConfigDict, Field


class StageCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    is_final: bool = False


class StageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    name: str
    position: int
    is_final: bool = Field(validation_alias="is_completed_stage")
