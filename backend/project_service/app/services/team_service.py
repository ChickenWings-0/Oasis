from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from ..models import Team, TeamInvite, TeamInviteStatus, TeamMember, TeamRole
from ..repositories import TeamRepository


class TeamService:
    """Business logic layer for team collaboration."""

    def __init__(self, db: Session):
        self.db = db
        self.team_repo = TeamRepository(db)

    def create_team(self, current_user_id: int, name: str) -> Team:
        if not name or len(name.strip()) == 0:
            raise ValidationError("Team name cannot be empty")
        if len(name) > 255:
            raise ValidationError("Team name must be <= 255 characters")

        try:
            return self.team_repo.create_team_with_owner_member(name=name.strip(), owner_id=current_user_id)
        except IntegrityError:
            raise ValidationError("Team creation failed due to conflicting data")
        except SQLAlchemyError:
            raise RuntimeError("Database error while creating team")

    def list_user_teams(self, current_user_id: int) -> list[Team]:
        return self.team_repo.list_user_teams(current_user_id)

    def invite_member(self, team_id: int, current_user_id: int, invited_user_id: int) -> TeamInvite:
        team = self.team_repo.get_team_by_id(team_id)
        if not team:
            raise NotFoundError(f"Team {team_id} not found")

        requester_member = self.team_repo.get_member(team_id=team_id, user_id=current_user_id)
        if not requester_member:
            raise ForbiddenError("Only team members can invite users")

        if requester_member.role not in {TeamRole.OWNER, TeamRole.ADMIN}:
            raise ForbiddenError("Only owner/admin can invite users")

        if invited_user_id == current_user_id:
            raise ValidationError("Cannot invite yourself")

        existing_member = self.team_repo.get_member(team_id=team_id, user_id=invited_user_id)
        if existing_member:
            raise ValidationError("User is already a team member")

        existing_invite = self.team_repo.get_invite_by_team_and_user(team_id=team_id, invited_user_id=invited_user_id)
        if existing_invite:
            raise ValidationError("Invite already exists for this user in this team")

        try:
            return self.team_repo.create_invite(team_id=team_id, invited_user_id=invited_user_id, invited_by=current_user_id)
        except IntegrityError:
            raise ValidationError("Invite already exists or user is already a team member")
        except SQLAlchemyError:
            raise RuntimeError("Database error while creating invite")

    def list_pending_invites(self, current_user_id: int) -> list[TeamInvite]:
        return self.team_repo.list_pending_invites_for_user(current_user_id)

    def accept_invite(self, invite_id: int, current_user_id: int) -> TeamMember:
        invite = self.team_repo.get_invite_by_id(invite_id)
        if not invite:
            raise NotFoundError(f"Invite {invite_id} not found")

        if invite.invited_user_id != current_user_id:
            raise ForbiddenError("You can only accept your own invites")

        if invite.status != TeamInviteStatus.PENDING:
            raise ValidationError("Only pending invites can be accepted")

        existing_member = self.team_repo.get_member(team_id=invite.team_id, user_id=current_user_id)
        if existing_member:
            raise ValidationError("You are already a team member")

        try:
            member = self.team_repo.accept_invite_and_add_member(invite_id=invite.id, user_id=current_user_id)
            if member is None:
                raise NotFoundError(f"Invite {invite_id} not found")
            return member
        except IntegrityError:
            raise ValidationError("User is already a team member")
        except SQLAlchemyError:
            raise RuntimeError("Database error while accepting invite")

    def decline_invite(self, invite_id: int, current_user_id: int) -> TeamInvite:
        invite = self.team_repo.get_invite_by_id(invite_id)
        if not invite:
            raise NotFoundError(f"Invite {invite_id} not found")

        if invite.invited_user_id != current_user_id:
            raise ForbiddenError("You can only decline your own invites")

        if invite.status != TeamInviteStatus.PENDING:
            raise ValidationError("Only pending invites can be declined")

        try:
            updated = self.team_repo.update_invite_status(invite.id, TeamInviteStatus.DECLINED)
            if not updated:
                raise NotFoundError(f"Invite {invite_id} not found")
            return updated
        except SQLAlchemyError:
            raise RuntimeError("Database error while declining invite")

    def list_members(self, team_id: int, current_user_id: int) -> list[TeamMember]:
        team = self.team_repo.get_team_by_id(team_id)
        if not team:
            raise NotFoundError(f"Team {team_id} not found")

        requester_member = self.team_repo.get_member(team_id=team_id, user_id=current_user_id)
        if not requester_member:
            raise ForbiddenError("Only team members can view team members")

        return self.team_repo.list_members(team_id)
