from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True, extra="forbid")

    categoryId: int = Field(gt=0, le=9223372036854775807)
    title: str = Field(min_length=1, max_length=100)
    desc: str = Field(min_length=1, max_length=100)
    duration: int = Field(ge=30, le=180)
    price: float = Field(gt=0, allow_inf_nan=False)
