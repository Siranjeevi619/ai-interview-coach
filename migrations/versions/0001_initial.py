"""create interview management tables"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "interviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("candidate_id", sa.String(36), sa.ForeignKey("candidates.id")),
        sa.Column("role", sa.String(120), nullable=False),
        sa.Column("difficulty", sa.String(12), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("cancelled_at", sa.DateTime()),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "interview_id",
            sa.String(36),
            sa.ForeignKey("interviews.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(120)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("interview_id", "sequence_number"),
    )
    op.create_table(
        "answers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "question_id",
            sa.String(36),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("interviews")
    op.drop_table("candidates")
