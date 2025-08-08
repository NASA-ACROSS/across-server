"""add data ingestion service account

Revision ID: 0f1706aa008d
Revises: 2571fe13c7ed
Create Date: 2025-08-08 11:55:24.953825

"""

import uuid
from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm, select

from across_server.core import config
from across_server.util.ssm import SSM
from migrations.build_records import service_account
from migrations.versions._2025_05_06_1129_043885e1cd78_permissions_and_roles_data import (
    role_data,
)
from migrations.versions.model_snapshots import models_2025_08_08 as models

# revision identifiers, used by Alembic.
revision: str = "0f1706aa008d"
down_revision: Union[str, None] = "2571fe13c7ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SERVICE_ACCOUNT_DATA = service_account.ServiceAccountData(
    id=uuid.UUID("9798d4e2-fe46-4da9-8708-dd098c27ea8c"),
    name="Data Ingestion Service Account",
    description="The service account that is used by the data ingestion service to push system information such as observatory schedules.",
)


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # for non-local the ID will be stored in param store for added security
    if not config.is_local():
        SERVICE_ACCOUNT_DATA.id = uuid.uuid4()

    record, secret = service_account.build(SERVICE_ACCOUNT_DATA, models.ServiceAccount)

    if not config.is_local():
        SSM.put_parameter(
            str(SERVICE_ACCOUNT_DATA.id),
            config.DATA_INGESTION_SERVICE_ACCOUNT_ID_PATH,
            config.APP_ENV,
            overwrite=True,
        )
        SSM.put_parameter(
            secret.key,
            config.DATA_INGESTION_INGESTION_SERVICE_ACCOUNT_SECRET_PATH,
            config.APP_ENV,
            type="SecureString",
            overwrite=True,
        )

    # assign roles to the service account -- must be done separately since
    # sqlalchemy expects db records, not new instantiations or IDs
    # get role records from the db
    roles = session.scalars(
        select(models.Role).filter_by(id=role_data["system_role"]["id"])
    )

    record.roles = list(roles.all())

    session.add(record)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    id = SERVICE_ACCOUNT_DATA.id

    if not config.is_local():
        # pull the created ID from the param store
        id = uuid.UUID(
            SSM.get_parameter(
                config.DATA_INGESTION_SERVICE_ACCOUNT_ID_PATH, config.APP_ENV
            )
        )

    account = session.scalar(select(models.ServiceAccount).filter_by(id=id))

    session.delete(account)
    session.commit()
