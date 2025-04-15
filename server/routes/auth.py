from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
import bcrypt

from models.user import User
from pydantic_schemas.user_create import UserCreate
from pydantic_schemas.user_login import UserLogin
from database import get_db

# Define the router for all authentication-related endpoints
router = APIRouter()

@router.post("/signup", status_code=201)
def signup_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    
    Steps:
    - Check if a user with the same email already exists.
    - Hash the user's password using bcrypt.
    - Generate a unique ID and create a new user entry.
    - Save the user in the database and return the new user object.
    """
    # Check for duplicate user by email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email already exists."
        )

    # Securely hash the user's password
    hashed_password = bcrypt.hashpw(
        user.password.encode(), bcrypt.gensalt(12)
    )

    # Create new user object with UUID
    new_user = User(
        id=str(uuid4()),
        name=user.name,
        email=user.email,
        password=hashed_password
    )

    # Add new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates an existing user.
    
    Steps:
    - Check if the user exists by their email.
    - Use bcrypt to verify the hashed password.
    - Return the user object if authentication is successful.
    """
    # Fetch user by email
    user_db = db.query(User).filter(User.email == user.email).first()
    if not user_db:
        raise HTTPException(
            status_code=400, 
            detail="User with this email does not exist."
        )

    # Compare plaintext password with stored hash
    if not bcrypt.checkpw(user.password.encode(), user_db.password):
        raise HTTPException(
            status_code=400, 
            detail="Incorrect password."
        )

    return user_db
