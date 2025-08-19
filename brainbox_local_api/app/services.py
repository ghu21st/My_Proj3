from pathlib import Path
import uuid, time

class LocalMockAws:
    """Simulates S3 (uploads/) and Glue (glue/ markers)."""
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_root = self.project_root / "local_state"
        self.uploads = self.state_root / "uploads"
        self.glue = self.state_root / "glue"
        self.uploads.mkdir(parents=True, exist_ok=True)
        self.glue.mkdir(parents=True, exist_ok=True)

    def put_csv(self, content: bytes, filename: str | None = None) -> Path:
        name = filename or f"upload__{uuid.uuid4().hex}.csv"
        path = self.uploads / name
        path.write_bytes(content)
        return path

    def trigger_glue_crawler(self, crawler_name: str = "bills_crawler") -> Path:
        marker = self.glue / f"{crawler_name}__{int(time.time())}__{uuid.uuid4().hex}.marker"
        marker.write_text("ok")
        return marker
