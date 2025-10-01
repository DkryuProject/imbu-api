from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RefreshTokenCompanyMng(Base):
    __tablename__ = "refresh_token_company_mng"

    company_code = Column(String(30), primary_key=True, index=True)
    token_mng_code = Column(String(30), primary_key=True, index=True)
    seq_app_mng = Column(String(9), primary_key=True, index=True)

    refresh_token = Column(String(100))
    access_token = Column(String(5000))
    token_expire_time = Column(String(50))  # "+3599초" 형태
