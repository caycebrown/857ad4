from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Integer, String

from api.database import Base

class Upload(Base):
    """Uploads Table"""

    __tablename__ = "uploads"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    file_name = Column(String, primary_key=True, index=True)
    number_of_rows = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)

    user = relationship("User", back_populates="uploads", foreign_keys=[user_id])
    prospects = relationship("Prospect", back_populates="uploads")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.id} | {self.file_name}"