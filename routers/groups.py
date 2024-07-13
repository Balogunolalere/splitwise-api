from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from database import groups_db
from auth import get_current_user
import uuid

router = APIRouter(prefix="/groups", tags=["groups"])

class GroupCreate(BaseModel):
    name: str

class GroupUpdate(BaseModel):
    name: str

class Group(BaseModel):
    id: str
    name: str
    members: List[str]

@router.post("/", response_model=Group)
async def create_group(group: GroupCreate, current_user: dict = Depends(get_current_user)):
    group_id = str(uuid.uuid4())
    new_group = {
        "id": group_id,
        "name": group.name,
        "members": [current_user["username"]]
    }
    groups_db.put(new_group, key=group_id)
    return Group(**new_group)

@router.get("/", response_model=List[Group])
async def get_user_groups(current_user: dict = Depends(get_current_user)):
    all_groups = groups_db.fetch().items
    user_groups = [Group(**group) for group in all_groups if current_user["username"] in group["members"]]
    return user_groups

@router.get("/{group_id}", response_model=Group)
async def get_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    return Group(**group)

@router.put("/{group_id}", response_model=Group)
async def update_group(group_id: str, group_update: GroupUpdate, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    group["name"] = group_update.name
    groups_db.put(group, key=group_id)
    return Group(**group)

@router.delete("/{group_id}")
async def delete_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    groups_db.delete(group_id)
    return {"message": "Group deleted successfully"}

@router.post("/{group_id}/members/{username}")
async def add_member_to_group(group_id: str, username: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    if username in group["members"]:
        raise HTTPException(status_code=400, detail="User already in group")
    group["members"].append(username)
    groups_db.put(group, key=group_id)
    return {"message": "Member added successfully"}

@router.delete("/{group_id}/members/{username}")
async def remove_member_from_group(group_id: str, username: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    if username not in group["members"]:
        raise HTTPException(status_code=400, detail="User not in group")
    group["members"].remove(username)
    groups_db.put(group, key=group_id)
    return {"message": "Member removed successfully"}