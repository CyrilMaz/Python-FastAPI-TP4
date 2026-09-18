from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from fastapi import FastAPI

class AccountType(str, Enum):
    INDIVIDUAL = "individual"
    PROFESSIONAL = "professional"

class User(BaseModel):
    id: int
    username: str = Field(min_length=3, max_length=30)
    email: str
    @field_validator("email")
    @classmethod
    def check_email(cls, value):
        if " " in value:
            raise ValueError("L'email ne doit pas contenir d'espace")
        return value

    
    phone: str | None = None
    account_type: AccountType
    is_active: bool = True

    @model_validator(mode="after")
    def check_professional_phone(self):
        if (
            self.account_type == AccountType.PROFESSIONAL
            and self.phone is None
        ):
            raise ValueError(
                "Un compte professionnel doit avoir un numéro de téléphone"
            )

        return self

users_db: dict[int, User] = {}

app = FastAPI()

@app.post("/users")
def create_user(user: User):
    users_db[user.id] = user
    return user