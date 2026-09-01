from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv
import os

_DEFAULT_INSURANCE_PDF_PATHS = [
    "documents/GTB_standard_Nov23.pdf",
    "documents/GTB_gold_Nov23.pdf",
    "documents/GTB_platinum_Nov23.pdf",
]


@dataclass(frozen=True)
class Settings:
    model_name: Optional[str]
    effort: Optional[str]
    insurance_pdf_paths: List[str] = field(default_factory=lambda: list(_DEFAULT_INSURANCE_PDF_PATHS))


def load_settings() -> Settings:
    load_dotenv()
    pdf_paths_env = os.getenv("INSURANCE_PDF_PATHS")
    return Settings(
        model_name=os.getenv("CLAUDE_MODEL"),
        effort=os.getenv("CLAUDE_EFFORT"),
        insurance_pdf_paths=(
            [path.strip() for path in pdf_paths_env.split(",") if path.strip()]
            if pdf_paths_env
            else list(_DEFAULT_INSURANCE_PDF_PATHS)
        ),
    )
