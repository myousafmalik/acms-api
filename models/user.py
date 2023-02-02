from sqlalchemy import Column, String, Integer, func, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship

from controller.database import Base


class User(Base):
    __tablename__ = 'user'
    user_id = Column(String(50), primary_key=True, index=True)
    email = Column(String(100))
    password = Column(String(250))
    is_active = Column(BOOLEAN, default=1)
    role_id = Column(Integer, ForeignKey('role.id'))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())
    user_to_role = relationship("Role", back_populates="role_to_user")
