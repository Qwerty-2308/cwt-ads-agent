"""Agent 3 tool — fetches product data from Google Drive or local fallback."""

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..config import GDRIVE_FOLDER_ID, DATA_DIR
from ..utils import get_logger

logger = get_logger(__name__)

# Optional GDrive imports — graceful if not configured
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False


class GDriveInput(BaseModel):
    query: str = Field(
        default="product data",
        description="What product information to fetch.",
    )


class GDriveTool(BaseTool):
    name: str = "gdrive_product_data"
    description: str = (
        "Fetches CrowdWisdomTrading product data, unique selling points, and audience "
        "information from Google Drive (or local fallback file). "
        "Returns the full product context as text."
    )
    args_schema: Type[BaseModel] = GDriveInput

    def _run(self, query: str = "product data") -> str:
        if GDRIVE_FOLDER_ID and GDRIVE_AVAILABLE:
            try:
                return self._fetch_from_gdrive()
            except Exception as exc:
                logger.warning("GDrive fetch failed (%s) — using local fallback", exc)

        return self._local_fallback()

    def _fetch_from_gdrive(self) -> str:
        """Fetch markdown/text files from the configured GDrive folder."""
        creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        service = build("drive", "v3", credentials=creds)

        results = (
            service.files()
            .list(
                q=f"'{GDRIVE_FOLDER_ID}' in parents and trashed=false",
                fields="files(id, name, mimeType)",
            )
            .execute()
        )
        files = results.get("files", [])
        logger.info("GDrive files found: %d", len(files))

        content_parts = []
        for file in files[:5]:  # limit to 5 files
            if "text" in file["mimeType"] or "document" in file["mimeType"]:
                req = service.files().get_media(fileId=file["id"])
                buf = io.BytesIO()
                downloader = MediaIoBaseDownload(buf, req)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                content_parts.append(f"# {file['name']}\n{buf.getvalue().decode()}")

        return "\n\n---\n\n".join(content_parts) if content_parts else self._local_fallback()

    def _local_fallback(self) -> str:
        """Read local product_data.md when GDrive is not configured."""
        local_path = DATA_DIR / "product_data.md"
        if local_path.exists():
            logger.info("Using local product data: %s", local_path)
            return local_path.read_text()
        return "No product data available. Use general CrowdWisdomTrading context."
