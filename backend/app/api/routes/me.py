from fastapi import APIRouter, Depends

from app.schemas.common import UserOut
from app.utils.deps import get_current_user

router = APIRouter(tags=["me"])


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user
