import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.applications.models import Application
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.imports.models import ShortlistImport, ShortlistImportRow
from app.modules.students.models import StudentProfile
from app.modules.users.models import User


class ImportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_opportunity(self, opportunity_id: uuid.UUID) -> HiringOpportunity | None:
        return self.db.get(HiringOpportunity, opportunity_id)

    def list_applications(self, opportunity_id: uuid.UUID) -> list[Application]:
        stmt = select(Application).where(
            Application.hiring_opportunity_id == opportunity_id
        )
        return list(self.db.scalars(stmt).all())

    def get_profiles_by_ids(
        self,
        profile_ids: list[uuid.UUID],
    ) -> list[StudentProfile]:
        if not profile_ids:
            return []
        stmt = (
            select(StudentProfile)
            .options(selectinload(StudentProfile.personal_information))
            .where(StudentProfile.id.in_(profile_ids))
        )
        return list(self.db.scalars(stmt).all())

    def get_users_by_ids(self, user_ids: list[uuid.UUID]) -> list[User]:
        if not user_ids:
            return []
        stmt = select(User).where(User.id.in_(user_ids))
        return list(self.db.scalars(stmt).all())

    def get_import(
        self,
        import_id: uuid.UUID,
        opportunity_id: uuid.UUID | None = None,
    ) -> ShortlistImport | None:
        stmt = (
            select(ShortlistImport)
            .options(selectinload(ShortlistImport.rows))
            .where(ShortlistImport.id == import_id)
        )
        if opportunity_id is not None:
            stmt = stmt.where(ShortlistImport.hiring_opportunity_id == opportunity_id)
        return self.db.scalars(stmt).first()

    def get_application(self, application_id: uuid.UUID) -> Application | None:
        return self.db.get(Application, application_id)

    def add(self, entity: object) -> None:
        self.db.add(entity)

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, entity: object) -> None:
        self.db.refresh(entity)
