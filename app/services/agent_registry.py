from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.database import AgentDB
from app.models import AgentRegistration, AgentStatus, AgentUpdate
from datetime import datetime


class AgentRegistryService:
    def __init__(self, db: Session):
        self.db = db

    def register_agent(self, agent: AgentRegistration) -> AgentRegistration:
        db_agent = AgentDB(
            agent_id=agent.agent_id,
            name=agent.name,
            role=agent.role,
            status=agent.status,
            description=agent.description,
            capabilities=agent.capabilities,
        )
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return AgentRegistration.from_orm(db_agent)

    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        db_agent = self.db.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
        return AgentRegistration.from_orm(db_agent) if db_agent else None

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentRegistration]:
        query = self.db.query(AgentDB)
        if status:
            query = query.filter(AgentDB.status == status)
        return [AgentRegistration.from_orm(agent) for agent in query.all()]

    def update_agent(self, agent_id: str, update: AgentUpdate) -> Optional[AgentRegistration]:
        db_agent = self.db.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
        if not db_agent:
            return None
        
        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_agent, key, value)
        
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        return AgentRegistration.from_orm(db_agent)

    def activate_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        return self.update_agent(agent_id, AgentUpdate(status=AgentStatus.ACTIVE))

    def pause_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        return self.update_agent(agent_id, AgentUpdate(status=AgentStatus.PAUSED))

    def retire_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        return self.update_agent(agent_id, AgentUpdate(status=AgentStatus.RETIRED))

    def delete_agent(self, agent_id: str) -> bool:
        db_agent = self.db.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
        if db_agent:
            self.db.delete(db_agent)
            self.db.commit()
            return True
        return False
