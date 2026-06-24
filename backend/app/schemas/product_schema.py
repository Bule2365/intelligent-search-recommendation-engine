from pydantic import BaseModel, Field


class ProductOut(BaseModel):
    product_id: str
    title: str
    description: str
    category: str
    brand: str
    price: int
    stock: int
    rating: float
    num_reviews: int

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    total: int
    items: list[ProductOut]


class ProductDetailResponse(BaseModel):
    product: ProductOut
