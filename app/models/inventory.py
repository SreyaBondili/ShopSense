from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    current_stock = Column(Integer, default=0, nullable=False)
    warehouse = Column(String(100), default="Main Warehouse", nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    product = relationship("Product", back_populates="inventory")

    @property
    def status(self) -> str:
        if self.current_stock == 0:
            return "OUT OF STOCK"
        elif self.current_stock <= self.reorder_level:
            return "LOW STOCK"
        else:
            return "IN STOCK"

    def __repr__(self):
        return f"<Inventory id={self.inventory_id} product_id={self.product_id} stock={self.current_stock} status={self.status}>"
