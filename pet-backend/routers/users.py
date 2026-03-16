from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.users import UserCreate, UserLogin, UserResponse, Token
from auth_utils import get_password_hash, verify_password, create_access_token
from models.users import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# -----------------------------
# TEST ENDPOINT
# -----------------------------
@router.get("/test")
def test():
    return {"message": "Users router is working"}


# -----------------------------
# SIGNUP
# -----------------------------
@router.get("/signup")
def signup_get_info():
    return {"message": "This endpoint requires a POST request with JSON data. Please use the signup form."}

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # try:
    #     # ✅ Updated password handling
    #     # Strip spaces and truncate to 72 characters (bcrypt max)
    #     password = user.password.strip()[:72]
    #     hashed_password = get_password_hash(password)

    #     new_user = User(
    #         name=user.name,
    #         email=user.email,
    #         location=user.location,
    #         password=hashed_password
    #     )

    #     db.add(new_user)
    #     db.commit()
    #     db.refresh(new_user)

    #     return new_user

    # except Exception as e:
    #     db.rollback()
    #     print(f"Signup Error: {e}")  # Log to console
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Signup failed: {str(e)}"
    #     )

    try:
        # ✅ Fixed: auth_utils.py now handles any password length securely
        hashed_password = get_password_hash(user.password)

        new_user = User(
            name=user.name,
            email=user.email,
            location=user.location,
            phone=user.phone,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception as e:
        db.rollback()
        print(f"Signup Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )

# -----------------------------
# LOGIN
# -----------------------------
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": db_user.name
    }


# -----------------------------
# GET ALL USERS
# -----------------------------
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# -----------------------------
# GET USER BY ID
# -----------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# -----------------------------
# DELETE USER
# -----------------------------
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
