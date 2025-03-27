from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr

# Import necessary modules and functions
from ...schemas.User.user_login_schema import LoginRequest, LoginResponse, otp_verification
from ...db.database import get_db, redis_client
from ...models.User.user_register import Register
from ...models.Events.Events import Event
from ...core.security import hash, create_access_token, verify_access
from ...bgjobs.auth import send_email_task
import random, hashlib

# Initialize router
router = APIRouter()

# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to hash OTP
def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

# Blacklisted tokens storage
blacklisted_tokens = set()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/verify-otp')

# Function to get the current authenticated user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if token in blacklisted_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Has Been Revoked")

    payload = verify_access(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    UserName = payload.get("sub")
    if UserName is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = db.query(Register).filter(Register.UserName == UserName).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Token")

    return user

# Route to handle user login with OTP verification
@router.post("/app/login-person")
def login_person(
    loginuser: LoginRequest = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(Register).filter(
        (Register.UserName == loginuser.identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Password verification based on role
    if user.Role_Name == "User":
        if not hash.verify(loginuser.Password, user.Password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
    else:
        if not (user.Password == loginuser.Password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

    try:
        # Generate and hash OTP
        otp = generate_otp()
        hashed_otp = hash_otp(otp)
        redis_client.setex(str(user.Email_ID), 300, hashed_otp)
        send_email_task.delay(user.Email_ID, otp)

        return {"Message" : f"Otp sent to the {user.Email_ID} Successfylly"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/verify-otp")
def verify_otp(otp_verification : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.query(Register).filter(
        (Register.Email_ID == otp_verification.username)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")


    # Verify OTP
    stored_hashed_otp = redis_client.get(str(user.Email_ID))
    if stored_hashed_otp and stored_hashed_otp == hash_otp(otp_verification.password):
        # redis_client.delete(str(user.Email_ID))

        # Generate access token
        access_token = create_access_token(data={
            "sub": user.UserName,
            "role": user.Role_Name,
            "id": user.UserID,
            "pp": user.Profile_Photo_Id
        })  # Remember this eventid is used for adding or getting participated user in that event

        return LoginResponse(
            UserName=user.UserName,
            Role_Name=user.Role_Name,
            access_token=access_token,
            token_type="bearer"
        )
    raise HTTPException(status_code=400, detail="Invalid OTP")

# Route to handle user logout
@router.post("/app/logout")
def log_out_user(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return {"Message": "Logged out Successfully"}


@router.post("/app/forgot-password")
def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(Register).filter(Register.Email_ID == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")

    try:
        otp = generate_otp()
        hashed_otp = hash_otp(otp)
        redis_client.setex(str(email), 300, hashed_otp)
        send_email_task.delay(email, otp)

        return {"Message": f"OTP sent to {email} successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ---------------------- Reset Password ----------------------
@router.post("/app/reset-password")
def reset_password(email : EmailStr,otp : str, new_password : str ,db: Session = Depends(get_db)):
    user = db.query(Register).filter(Register.Email_ID == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_hashed_otp = redis_client.get(str(email))
    if not stored_hashed_otp or stored_hashed_otp != hash_otp(otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Hash the new password and update it in the database
    user.Password = hash.hashing(new_password)
    db.commit()
    # redis_client.delete(email)

    return {"Message": "Password reset successfully"}
