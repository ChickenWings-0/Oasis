from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import Team, TeamInvite, TeamInviteStatus, TeamMember, TeamRole


class TeamRepository:
    """Database access layer for team collaboration entities."""

    def __init__(self, db: Session):
        self.db = db

    # Team CRUD
    def create_team(self, name: str, owner_id: int) -> Team:
        try:
            team = Team(name=name, owner_id=owner_id)
            self.db.add(team)
            self.db.commit()
            self.db.refresh(team)
            return team
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def create_team_with_owner_member(self, name: str, owner_id: int) -> Team:
        try:
            team = Team(name=name, owner_id=owner_id)
            self.db.add(team)
            self.db.flush()

            owner_member = TeamMember(team_id=team.id, user_id=owner_id, role=TeamRole.OWNER)
            self.db.add(owner_member)

            self.db.commit()
            self.db.refresh(team)
            return team
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_team_by_id(self, team_id: int) -> Team | None:
        return self.db.query(Team).filter(Team.id == team_id).first()

    def list_user_teams(self, user_id: int) -> list[Team]:
        return (
            self.db.query(Team)
            .outerjoin(TeamMember, TeamMember.team_id == Team.id)
            .filter(or_(Team.owner_id == user_id, TeamMember.user_id == user_id))
            .distinct()
            .order_by(Team.created_at.desc())
            .all()
        )

    # Team members CRUD
    def add_member(self, team_id: int, user_id: int, role: TeamRole = TeamRole.MEMBER) -> TeamMember:
        try:
            member = TeamMember(team_id=team_id, user_id=user_id, role=role)
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return member
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_member(self, team_id: int, user_id: int) -> TeamMember | None:
        return (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            .first()
        )

    def list_members(self, team_id: int) -> list[TeamMember]:
        return (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id)
            .order_by(TeamMember.joined_at.asc())
            .all()
        )

    # Team invites CRUD
    def create_invite(self, team_id: int, invited_user_id: int, invited_by: int) -> TeamInvite:
        try:
            invite = TeamInvite(
                team_id=team_id,
                invited_user_id=invited_user_id,
                invited_by=invited_by,
                status=TeamInviteStatus.PENDING,
            )
            self.db.add(invite)
            self.db.commit()
            self.db.refresh(invite)
            return invite
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_invite_by_id(self, invite_id: int) -> TeamInvite | None:
        return self.db.query(TeamInvite).filter(TeamInvite.id == invite_id).first()

    def get_invite_by_team_and_user(self, team_id: int, invited_user_id: int) -> TeamInvite | None:
        return (
            self.db.query(TeamInvite)
            .filter(TeamInvite.team_id == team_id, TeamInvite.invited_user_id == invited_user_id)
            .first()
        )

    def list_pending_invites_for_user(self, user_id: int) -> list[TeamInvite]:
        return (
            self.db.query(TeamInvite)
            .filter(
                TeamInvite.invited_user_id == user_id,
                TeamInvite.status == TeamInviteStatus.PENDING,
            )
            .order_by(TeamInvite.created_at.desc())
            .all()
        )

    def update_invite_status(self, invite_id: int, status: TeamInviteStatus) -> TeamInvite | None:
        invite = self.get_invite_by_id(invite_id)
        if invite is None:
            return None

        try:
            invite.status = status
            self.db.commit()
            self.db.refresh(invite)
            return invite
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def accept_invite_and_add_member(self, invite_id: int, user_id: int) -> TeamMember | None:
        invite = self.get_invite_by_id(invite_id)
        if invite is None:
            return None

        try:
            invite.status = TeamInviteStatus.ACCEPTED
            member = TeamMember(team_id=invite.team_id, user_id=user_id, role=TeamRole.MEMBER)
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return member
        except SQLAlchemyError:
            self.db.rollback()
            raise


class TeamMemberRepository:
    """Focused repository for team membership lookups used by access control."""

    def __init__(self, db: Session):
        self.db = db

    def get_team_member(self, team_id: int, user_id: int) -> TeamMember | None:
        return (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            .first()
        )
