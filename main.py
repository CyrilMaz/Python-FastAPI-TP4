from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from fastapi import FastAPI, HTTPException


#################################
#          Classes USER         #
#################################


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

class UserPublic(BaseModel):
    id: int
    username: str
    account_type: AccountType
    is_active: bool

class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=30
    )
    email: str | None = None
    phone: str | None = None
    account_type: AccountType | None = None
    is_active: bool | None = None

    @field_validator("email")
    @classmethod
    def check_email(cls, value):
        if value is not None and " " in value:
            raise ValueError("L'email ne doit pas contenir d'espace")
        return value

users_db: dict[int, User] = {}

###################################
#          Classes Review         #
###################################

class ReviewStatus(str, Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"

class ReviewPhoto(BaseModel):
    url: str = Field(min_length=5, max_length=500)
    caption: str | None = Field(default=None, max_length=120)

###############################
#          Routes API         #
###############################

app = FastAPI()

@app.post("/users", response_model=UserPublic, status_code=201)
def create_user(user: User):
    if user.id in users_db:
        raise HTTPException(
            status_code=400,
            detail="Un utilisateur avec cet id existe déjà"
        )

    for existing_user in users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=400,
                detail="Cet email est déjà utilisé"
            )

    users_db[user.id] = user
    return user

@app.get("/users", response_model=list[UserPublic])
def get_users():
    return list(users_db.values())

@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    return users_db[user_id]

@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, update: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    changes = update.model_dump(exclude_unset=True)

    if "email" in changes:
        for existing_user in users_db.values():
            if (
                existing_user.id != user_id
                and existing_user.email == changes["email"]
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Cet email est déjà utilisé"
                )

    old_user = users_db[user_id]

    new_data = old_user.model_dump()
    new_data.update(changes)

    updated_user = User.model_validate(new_data)

    users_db[user_id] = updated_user
    return updated_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    del users_db[user_id]

    return {"message": "Utilisateur supprimé"}