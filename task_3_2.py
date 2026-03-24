from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(title="Задание 3.2")

products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    
app.get("/product/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

app.get("/products/search", response_model=List[Product])
async def search_products(
    keyword: str = Query(..., min_length=1, description="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество результатов")
):
    results = []
    for product in products:
        if keyword.lower() in product["name"].lower():
            if category is None or product["category"].lower() == category.lower():
                results.append(product)
    return results[:limit]