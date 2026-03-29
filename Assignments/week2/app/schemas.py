from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExtractBody(BaseModel):
    text: str = Field(..., description="Free-form notes to extract action items from.")
    save_note: bool = False

    @field_validator("text")
    @classmethod
    def strip_nonempty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("text is required")
        return s


class ExtractItemOut(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: list[ExtractItemOut]


class ActionItemOut(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str


class MarkDoneBody(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool


class CreateNoteBody(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def strip_content(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("content is required")
        return s


class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str
