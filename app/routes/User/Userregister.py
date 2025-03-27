from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
import os, shutil

# Importing necessary modules and dependencies
from ...schemas.User.user_register_schema import UserRegisterJson, UserResponse, UserUpdateRequest
from ...db.database import get_db
from ...core.security import hash
from ...schemas.User.user_register_schema import validate_file
from ...models.User.user_register import Register
from ...models.User.profile_photo import ProfilePhoto
from ...routes.User.Userlogin import get_current_user

router = APIRouter()

# User Registration Endpoint
@router.post("/create-user", response_model=UserResponse)
def create_user(
    user: UserRegisterJson = Depends(),
    uploaded_file: UploadFile = Depends(validate_file),
    db: Session = Depends(get_db),
):
    try:
        UPLOAD_DIR = "static"
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # Check if user already exists
        existing_user = db.query(Register).filter(
            (Register.UserName == user.UserName) | (Register.Email_ID == user.Email_ID)
        ).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Exists")

        # Hash the user's password
        hashed_password = hash.hashing(user.Password)

        # Save the profile photo
        file_ext = uploaded_file.filename.split(".")[-1]
        unique_filename = f"{user.UserName}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)

        new_profilephoto = ProfilePhoto(
            Photo_Url=f"/static/{unique_filename}",
            Photo_Type=uploaded_file.content_type
        )
        db.add(new_profilephoto)
        db.flush()  # Flush so we get the Photo ID

        # Create new user
        new_user = Register(
            FirstName=user.FirstName,
            LastName=user.LastName,
            UserName=user.UserName,
            Gender=user.Gender,
            Mobile_Number=user.Mobile_Number,
            Email_ID=user.Email_ID,
            Password=hashed_password,
            Profile_Photo_Id=new_profilephoto.Photo_ID
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse(
            User_ID=new_user.UserID,
            FirstName=new_user.FirstName,
            LastName=new_user.LastName,
            UserName=new_user.UserName,
            Gender=new_user.Gender,
            Mobile_Number=new_user.Mobile_Number,
            Email_ID=new_user.Email_ID,
            Profile_Photo_Id=new_profilephoto.Photo_ID
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error : {str(e)}")
    finally:
        db.close()

# Get All Users (Admin Only)
@router.get("/admin-dash/user/get-user", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name == "Admin":
        users = db.query(Register).all()
        return [UserResponse(
            User_ID=user.UserID,
            FirstName=user.FirstName,
            LastName=user.LastName,
            UserName=user.UserName,
            Gender=user.Gender,
            Mobile_Number=user.Mobile_Number,
            Email_ID=user.Email_ID,
            Profile_Photo_Id=user.Profile_Photo_Id
        ) for user in users]
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

# Get User by ID (Admin Only)
@router.get("/admin-dash/user/get-user/{ID}", response_model=UserResponse)
def get_by_id(ID: str, db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name == "Admin":
        user = db.query(Register).filter(Register.UserID == ID).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
        return UserResponse(
            User_ID=user.UserID,
            FirstName=user.FirstName,
            LastName=user.LastName,
            UserName=user.UserName,
            Gender=user.Gender,
            Mobile_Number=user.Mobile_Number,
            Email_ID=user.Email_ID,
            Profile_Photo_Id=user.Profile_Photo_Id
        )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

# Update User Profile (User Only)
@router.patch("/app/dash/user/update-user")
def update_user_details(
    update_request: UserUpdateRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    if current_user.Role_Name == "User":
        try:
            user = db.query(Register).filter(Register.UserName == update_request.UserName).first()
            if not user:
                raise HTTPException(status_code=404, detail="User Not Found")

            # Update the fields that are provided
            if update_request.FirstName:
                user.FirstName = update_request.FirstName
            if update_request.LastName:
                user.LastName = update_request.LastName
            if update_request.New_UserName:
                user.UserName = update_request.New_UserName
            if update_request.Gender:
                user.Gender = update_request.Gender
            if update_request.Mobile_Number:
                user.Mobile_Number = update_request.Mobile_Number
            if update_request.Email_ID:
                user.Email_ID = update_request.Email_ID

            db.commit()
            return {"Message": "Profile Details Updated Successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

# Delete User Profile (User Only)
@router.delete("/dash/user/{ID}")
def delete_user(ID: str, db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name == "User":
        try:
            user = db.query(Register).filter(Register.UserID == ID).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
            db.delete(user)
            db.commit()
            return {"Message": "User Deleted Successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
