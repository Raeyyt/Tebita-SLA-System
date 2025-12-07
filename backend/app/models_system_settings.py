from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class SystemSettings(Base):
    """System-wide configuration settings"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemSettings {self.setting_key}={self.setting_value}>"
