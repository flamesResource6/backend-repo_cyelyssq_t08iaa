from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# According to the platform guidelines, each model class corresponds to a collection
# with the collection name = class name lowercased.

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=20)
    avatar_url: Optional[str] = None
    created_at: Optional[str] = None


class Profile(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    full_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    disability_type: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None
    created_at: Optional[str] = None


class Provider(BaseModel):
    name: str
    specialty: Optional[str] = None
    rating: Optional[float] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None


class Appointment(BaseModel):
    user_id: str
    provider_id: str
    scheduled_for: str
    notes: Optional[str] = None


class MedicalRecord(BaseModel):
    user_id: str
    provider_id: Optional[str] = None
    title: str
    description: Optional[str] = None


class Post(BaseModel):
    user_id: str
    content: str
    images: Optional[List[str]] = None


class Group(BaseModel):
    name: str
    description: Optional[str] = None


class Program(BaseModel):
    title: str
    category: Optional[str] = None
    eligibility: Optional[str] = None


class Application(BaseModel):
    user_id: str
    program_id: str
    status: str = "draft"


class Product(BaseModel):
    name: str
    category: Optional[str] = None
    price: Optional[float] = None
    vendor_id: Optional[str] = None


class Vendor(BaseModel):
    name: str
    rating: Optional[float] = None


class Review(BaseModel):
    user_id: str
    product_id: str
    rating: int
    comment: Optional[str] = None
