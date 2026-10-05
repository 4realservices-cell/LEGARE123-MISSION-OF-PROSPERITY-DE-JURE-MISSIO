from sqlalchemy.orm import Session
from app.database import WorkflowDB
from app.models import WorkflowTemplate, WorkflowStep
from datetime import datetime
from typing import List, Optional


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def create_workflow(self, workflow_template: WorkflowTemplate) -> WorkflowTemplate:
        db_workflow = WorkflowDB(
            workflow_id=workflow_template.workflow_id,
            name=workflow_template.name,
            description=workflow_template.description,
            steps=[step.dict() for step in workflow_template.steps],
        )
        self.db.add(db_workflow)
        self.db.commit()
        self.db.refresh(db_workflow)
        return WorkflowTemplate.from_orm(db_workflow)

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowTemplate]:
        db_workflow = self.db.query(WorkflowDB).filter(WorkflowDB.workflow_id == workflow_id).first()
        return WorkflowTemplate.from_orm(db_workflow) if db_workflow else None

    def list_workflows(self) -> List[WorkflowTemplate]:
        workflows = self.db.query(WorkflowDB).all()
        return [WorkflowTemplate.from_orm(w) for w in workflows]

    def delete_workflow(self, workflow_id: str) -> bool:
        db_workflow = self.db.query(WorkflowDB).filter(WorkflowDB.workflow_id == workflow_id).first()
        if db_workflow:
            self.db.delete(db_workflow)
            self.db.commit()
            return True
        return False
