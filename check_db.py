import asyncio
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.base import async_session_maker
from sqlalchemy import select
from app.models.product import Product
from app.models.category import Category

async def main():
    async with async_session_maker() as session:
        prods = (await session.execute(select(Product))).scalars().all()
        cats = (await session.execute(select(Category))).scalars().all()
        
        print(f"Total Products: {len(prods)}")
        print(f"Active Products: {sum(1 for p in prods if not p.is_archived)}")
        print(f"Total Categories: {len(cats)}")

        if prods:
            print("Sample Product category_id:", prods[0].category_id)
            print("Sample Category ID:", cats[0].id)

if __name__ == "__main__":
    asyncio.run(main())
