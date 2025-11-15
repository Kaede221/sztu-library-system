from fastapi import APIRouter

router = APIRouter()


@router.get("/get-all-users")
def get_users():
    return {"message": "Get All Users"}
