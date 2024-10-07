# app/api/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models import Item
from app.schemas import ItemCreate, Item as ItemSchema, ItemResponse
from app.dependencies import (
    get_token_header,
    get_current_user,
    RoleChecker,
    log_request,
)
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models import Item, User

# V1

# router = APIRouter(
#     prefix="/api/v1/items", tags=["items"], dependencies=[Depends(get_token_header)]
# )

# @router.get("/items/{item_id}")
# async def read_item(
#     item_id: int,
#     commons: dict = Depends(common_parameters)
# ):
#     return {"item_id": item_id, **commons}

# @router.post("/items/")
# async def create_item(item: Item):
#     return item

# V2

# @router.post("/items/", response_model=ItemSchema)
# async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
#     db_item = Item(**item.model_dump())
#     db.add(db_item)
#     await db.commit()
#     await db.refresh(db_item)
#     return db_item

# @router.get("/items/{item_id}", response_model=ItemSchema)
# async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Item).filter(Item.id == item_id))
#     db_item = result.scalar_one_or_none()
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return db_item

# @router.get("/items/", response_model=list[ItemSchema])
# async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Item).offset(skip).limit(limit))
#     return result.scalars().all()

# @router.put("/items/{item_id}", response_model=ItemSchema)
# async def update_item(item_id: int, item: ItemCreate, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Item).filter(Item.id == item_id))
#     db_item = result.scalar_one_or_none()
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")

#     update_data = item.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_item, key, value)

#     await db.commit()
#     await db.refresh(db_item)
#     return db_item

# @router.delete("/items/{item_id}", response_model=ItemSchema)
# async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Item).filter(Item.id == item_id))
#     db_item = result.scalar_one_or_none()
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")

#     await db.delete(db_item)
#     await db.commit()
#     return db_item

router = APIRouter(
    prefix="/api/v1/items", tags=["items"], dependencies=[Depends(log_request)]
)

allow_create_item = RoleChecker(["admin", "editor"])


@router.post(
    "/", response_model=ItemResponse, dependencies=[Depends(allow_create_item)]
)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = Item(**item.dict(), owner_id=current_user.id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = await db.get(Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this item"
        )
    return db_item