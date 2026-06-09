from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List
from model.user.app_mm_user import AppMmUserCreate, AppMmUserUpdate, AppMmUserResponse
from service.user.app_mm_user_service import AppMmUserService
from model.api_response import ApiResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create", response_model=ApiResponse[AppMmUserResponse], status_code=status.HTTP_201_CREATED)
def create_user(user: AppMmUserCreate):
    """Create a new user"""
    try:
        result = AppMmUserService.create_user(user)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{user_id}", response_model=ApiResponse[AppMmUserResponse])
def get_user(user_id: UUID):
    """Get user by ID"""
    user = AppMmUserService.get_user_by_id(user_id)
    if not user:
        return ApiResponse.error({"message": "User not found"})
    return ApiResponse.success(user)

@router.get("/get-all", response_model=ApiResponse[List[AppMmUserResponse]])
def get_all_users():
    """Get all users"""
    users = AppMmUserService.get_all_users()
    return ApiResponse.success(users)

@router.put("/update/{user_id}", response_model=ApiResponse[AppMmUserResponse])
def update_user(user_id: UUID, user: AppMmUserUpdate):
    """Update user by ID"""
    updated_user = AppMmUserService.update_user(user_id, user)
    if not updated_user:
        return ApiResponse.error({"message": "User not found"})
    return ApiResponse.success(updated_user)

@router.delete("/delete-by-guid/{user_id}", response_model=ApiResponse[dict])
def delete_user(user_id: UUID):
    """Delete user by ID"""
    success = AppMmUserService.delete_user(user_id)
    if not success:
        return ApiResponse.error({"message": "User not found"})
    return ApiResponse.success({"message": "User deleted successfully"})
