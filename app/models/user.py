from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    VENDOR = "VENDOR"
    CUSTOMER = "CUSTOMER"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VENDOR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    vendor = relationship("Vendor", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User id={self.user_id} email={self.email} role={self.role}>"
