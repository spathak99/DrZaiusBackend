from pydantic import BaseModel


class CaregiverAccessUpdate(BaseModel):
    access_level: str


