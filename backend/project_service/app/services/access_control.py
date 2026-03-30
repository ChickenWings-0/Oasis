from sqlalchemy.orm import Session

from ..models import TeamRole
from ..repositories import TeamMemberRepository


def has_project_access(user_id: int, project, db: Session, require_role: str | None = None) -> bool:
    """
    Return True if user can access project.

    Access rules:
    - Project owner always has access.
    - Team member has access when project.team_id exists and membership exists.
    - If require_role is provided, enforce hierarchy: owner > admin > member.
    """
    if not project:
        return False

    if project.owner_id == user_id:
        return True

    team_id = getattr(project, "team_id", None)
    if not team_id:
        return False

    team_member_repo = TeamMemberRepository(db)
    membership = team_member_repo.get_team_member(team_id=team_id, user_id=user_id)
    if not membership:
        return False

    if require_role is None:
        return True

    role_priority = {
        "member": 1,
        "admin": 2,
        "owner": 3,
    }

    required = role_priority.get(str(require_role).lower())
    if required is None:
        return False

    member_role = membership.role.value if isinstance(membership.role, TeamRole) else str(membership.role)
    member_rank = role_priority.get(member_role.lower(), 0)

    return member_rank >= required
