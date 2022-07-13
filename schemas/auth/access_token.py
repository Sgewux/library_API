from pydantic import BaseModel, Field

class AccessToken(BaseModel):
    access_token: str = Field(...)
    token_type: str | None = Field('bearer')