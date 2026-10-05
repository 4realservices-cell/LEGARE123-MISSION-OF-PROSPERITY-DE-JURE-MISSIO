from typing import Dict, List, Optional
from app.models import AgentRegistration

class AgentRegistryService:
    def __init__(self):
        self._agents: Dict[str, AgentRegistration] = {}

    def register_agent(self, agent: AgentRegistration) -> AgentRegistration:
        self._agents[agent.agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        return self._agents.get(agent_id)

    def list_agents(self) -> List[AgentRegistration]:
        return list(self._agents.values())

agent_registry = AgentRegistryService()
