from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:

    # this is wrong, we should not return a default tentat
    # tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="No tenant associated with this user")

    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # total has 3 decimals (333.333 etc) and float() was turning it into a binary float,
    # then the frontend rounded that float, so it came out a few cents off sometimes
    # rounding once here to cents with Decimal (half up), should fix it
    total_revenue = Decimal(revenue_data['total']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_revenue_float = float(total_revenue)
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_float,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
