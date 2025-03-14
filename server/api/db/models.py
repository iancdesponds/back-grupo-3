from sqlalchemy import Column, Integer, String, ARRAY
from database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    options = Column(ARRAY(String), nullable=True)  # Apenas para múltipla escolha
    answer = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "multiple_choice" ou "coding"
    difficulty = Column(String, nullable=False)  # "fácil", "médio", "difícil"