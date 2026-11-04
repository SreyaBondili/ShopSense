from sqlalchemy import Column, Integer, String
from app.database import Base

class Category(Base):
    """
    Mentor Step 4: Category Hierarchy Model
    Represents product taxonomies (e.g. Electronics -> Mobile/Laptop, Fashion -> Men/Women).
    """
    __tablename__ = "categories"
    __table_args__ = {"extend_existing": True}

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(80), nullable=False)
    parent_category = Column(String(80), nullable=True)

    def __repr__(self):
        return f"<Category id={self.category_id} name={self.category_name} parent={self.parent_category}>"
