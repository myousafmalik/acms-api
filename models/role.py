from sqlalchemy import Column, String, Integer, func, TIMESTAMP
from sqlalchemy.orm import relationship

from controller.database import Base


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(25))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())
    role_to_user = relationship("Role", back_populates="user_to_role")

