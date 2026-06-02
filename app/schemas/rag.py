from pydantic import Field

from app.schemas.common import Citation, StrictBaseModel


class PolicyDocument(StrictBaseModel):
    doc_id: str
    doc_name: str
    doc_type: str
    content: str
    metadata: dict = Field(default_factory=dict)
    source_path: str


class DocumentChunk(StrictBaseModel):
    chunk_id: str
    doc_id: str
    doc_name: str
    doc_type: str
    section_heading: str
    text: str
    metadata: dict = Field(default_factory=dict)
    source_path: str


class RetrievalHit(StrictBaseModel):
    chunk_id: str
    text: str
    score: float
    citation: Citation
    metadata: dict = Field(default_factory=dict)