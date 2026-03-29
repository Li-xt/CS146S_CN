from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemOut,
    ExtractBody,
    ExtractItemOut,
    ExtractResponse,
    MarkDoneBody,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(body: ExtractBody) -> ExtractResponse:
    note_id: Optional[int] = None
    if body.save_note:
        note_id = db.insert_note(body.text)
    try:
        items = extract_action_items_llm(body.text)
    except ValueError as exc:
        detail = str(exc)
        if "Missing API key" in detail:
            raise HTTPException(status_code=503, detail=detail) from exc
        raise HTTPException(
            status_code=502, detail="LLM extraction failed or returned invalid JSON"
        ) from exc
    ids = db.insert_action_items(items, note_id=note_id)
    out_items = [ExtractItemOut(id=i, text=t) for i, t in zip(ids, items)]
    return ExtractResponse(note_id=note_id, items=out_items)


@router.post("/extract", response_model=ExtractResponse)
def extract(body: ExtractBody) -> ExtractResponse:
    note_id: Optional[int] = None
    if body.save_note:
        note_id = db.insert_note(body.text)

    items = extract_action_items(body.text)
    ids = db.insert_action_items(items, note_id=note_id)
    out_items = [ExtractItemOut(id=i, text=t) for i, t in zip(ids, items)]
    return ExtractResponse(note_id=note_id, items=out_items)


@router.get("", response_model=list[ActionItemOut])
def list_all(note_id: Optional[int] = None) -> list[ActionItemOut]:
    rows = db.list_action_items(note_id=note_id)
    return [ActionItemOut.model_validate(db.action_item_row_to_dict(r)) for r in rows]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, body: MarkDoneBody) -> MarkDoneResponse:
    updated = db.mark_action_item_done(action_item_id, body.done)
    if not updated:
        raise HTTPException(status_code=404, detail="action item not found")
    return MarkDoneResponse(id=action_item_id, done=body.done)
