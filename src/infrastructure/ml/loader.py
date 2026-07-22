import asyncio
import json
import joblib
from pathlib import Path
from typing import Dict, List, Any, Optional


class ModelArtifactLoader:
    
    """Loads and retains the artifacts in memory for the application lifetime/lifecycle"""

    def __init__(
        self,
        model_path: str,
        metadata_path: str,
        schema_path: str
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.schema_path = Path(schema_path)
        self._model: Any = None
        self._schema: Dict = {}
        self._metadata: Dict = {}


    async def load(self) -> None:
        for path in (self.model_path, self.metadata_path, self.schema_path):
            if not path.exists():
                raise FileNotFoundError(f"Missing: {path}")

        self._model, self._metadata, self._schema = joblib.load(self.model_path), self._read_json(self.metadata_path), self._read_json(self.schema_path)

    async def unload(self) -> None:
        self._model = None
        self._metadata = {}
        self._schema = {}

    def _read_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf=8") as file:
            return json.load(file)

    @property
    def model(self) -> object:
        if self._model is None:
            raise RuntimeError("Model has not loaded, call load() during app startup")

        return self._model

    @property
    def metadata(self) -> Dict[str, Any]:
        if self._metadata is None:
            raise RuntimeError("Metadata has not loaded, call load() during app startup")

        return self._metadata

    @property
    def schema(self) -> Dict[str, Any]:
        if self._schema is None:
            raise RuntimeError("Schema has not loaded, call load() during app startup")

        return self._schema


    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    
