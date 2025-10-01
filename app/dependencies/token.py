import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends

from .database import get_db
from app.models.token import RefreshTokenCompanyMng

CLIENT_ID = os.getenv("APS_CLIENT_ID", "your_client_id")
CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET", "your_client_secret")
TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token"


async def get_token(
        db: Session = Depends(get_db),
) -> str:
    token_row = db.query(RefreshTokenCompanyMng).filter_by(
        company_code="COMPANY00004",
        token_mng_code="ad",
        seq_app_mng="appAd0001"
    ).first()

    return token_row.access_token
