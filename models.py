"""
Common pydantic models used in the application
"""

from datetime import datetime

from pydantic import BaseModel


class Coefficients(BaseModel):
    a: int
    b: int


class Measurement(BaseModel):
    timestamp: datetime
    value: int
