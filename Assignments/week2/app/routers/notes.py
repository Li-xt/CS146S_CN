from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import CreateNoteBody, NoteOut


router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteOut])
def list_notes() -> list[NoteOut]:
    rows = db.list_notes()
    return [NoteOut.model_validate(db.note_row_to_dict(r)) for r in rows]


@router.post("", response_model=NoteOut)
def create_note(body: CreateNoteBody) -> NoteOut:
    note_id = db.insert_note(body.content)
    note = db.get_note(note_id)
    assert note is not None
    return NoteOut.model_validate(db.note_row_to_dict(note))


@router.get("/{note_id}", response_model=NoteOut)
def get_single_note(note_id: int) -> NoteOut:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteOut.model_validate(db.note_row_to_dict(row))
