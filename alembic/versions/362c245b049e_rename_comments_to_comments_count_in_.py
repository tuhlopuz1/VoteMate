"""rename comments to comments_count in Poll

Revision ID: 362c245b049e
Revises: 93474f003702
Create Date: 2025-07-10 10:28:43.747206

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "362c245b049e"
down_revision: Union[str, Sequence[str], None] = "93474f003702"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
