"""initial migration

Revision ID: 93474f003702
Revises:
Create Date: 2025-07-10 10:17:48.781361

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "93474f003702"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
