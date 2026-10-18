from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id", ondelete="RESTRICT"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    product = relationship("Product", back_populates="transactions")
    vendor = relationship("Vendor", back_populates="transactions")
    user = relationship("User", backref="transactions")

    def __repr__(self):
        return f"<Transaction id={self.transaction_id} product_id={self.product_id} qty={self.quantity} amount={self.amount}>"
