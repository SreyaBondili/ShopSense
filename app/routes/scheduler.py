from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Any, Optional
from app.utils.security import get_current_active_user, require_admin
from app.models.user import User
from app.scheduler.scheduler_service import workflow_scheduler

router = APIRouter(prefix="/api/scheduler", tags=["Workflow Automation"])

@router.get("/status")
def get_scheduler_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Module 4 & 9: View APScheduler workflow reliability, execution status, and job schedule."""
    return workflow_scheduler.get_workflow_status()

@router.post("/trigger")
def trigger_workflow_manually(
    job_type: str = Query("all", description="Job type to trigger: 'retrain', 'analytics', 'all', or 'test_failure'"),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Module 4 & 9: Manually trigger automated workflow execution for demonstration & validation."""
    return workflow_scheduler.trigger_workflow_manually(job_type)
