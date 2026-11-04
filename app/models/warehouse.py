from sqlalchemy import Column, Integer, String
from app.database import Base

class Warehouse(Base):
    """
    Mentor Step 3: Warehouse Table
    Maintains warehouse repositories and depot locations.
    """
    __tablename__ = "warehouse"
    __table_args__ = {"extend_existing": True}

    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Warehouse id={self.warehouse_id} name={self.warehouse_name} location={self.location}>"
