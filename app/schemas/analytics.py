from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class MarketplaceSummary(BaseModel):
    total_revenue: float
    total_transactions: int
    total_quantity_sold: int
    average_transaction_value: float
    total_vendors: int
    total_products: int

class VendorPerformanceItem(BaseModel):
    vendor_id: int
    business_name: str
    owner_name: str
    category: str
    status: str
    total_revenue: float
    total_transactions: int
    total_quantity_sold: int
    product_count: int

class ProductPerformanceItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    vendor_id: int
    vendor_name: str
    price: float
    total_revenue: float
    quantity_sold: int
    current_stock: int
    inventory_status: str

class RevenueTrendItem(BaseModel):
    date: str
    revenue: float
    transactions_count: int
    quantity_sold: int

class CategoryPerformanceItem(BaseModel):
    category: str
    revenue: float
    units_sold: int
    products_count: int

class AnalyticsDashboardResponse(BaseModel):
    summary: MarketplaceSummary
    vendor_performance: List[VendorPerformanceItem]
    product_performance: List[ProductPerformanceItem]
    revenue_trend: List[RevenueTrendItem]
    category_performance: List[CategoryPerformanceItem]
