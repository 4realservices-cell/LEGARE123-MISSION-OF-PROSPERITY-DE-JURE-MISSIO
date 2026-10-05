# RBAC and Permissions Guide

## Role Definitions

### Admin
- Full system access
- User management
- Policy configuration
- Audit log access
- All CRUD operations on agents, evidence, claims

### Operator
- Register agents
- Submit and verify evidence
- Evaluate claims
- View audit logs
- Can modify resources they created

### Viewer
- Read-only access to:
  - Agent listings
  - Claims and their timelines
  - Evidence listings
  - Audit logs

## Enforcing Permissions

Permissions are enforced at the API level using the `require_roles()` decorator.

### Example: Admin-only endpoint
```python
@app.post("/api/v1/auth/register", response_model=dict)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    # Only admins can register new users
    ...
```

### Example: Operator or Admin
```python
@app.post("/api/v1/agents")
def register_agent(
    agent: AgentRegistration,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "operator"))
):
    # Admins and operators can register agents
    ...
```

## Audit Trail
Every privileged action is logged with:
- Actor (username)
- Action (register_agent, verify_evidence, etc.)
- Target resource ID
- Timestamp
- Details

## Future Enhancements
- Fine-grained permissions (e.g., can_verify_security_evidence)
- Resource-level access control
- Policy templates
- Permission delegation
