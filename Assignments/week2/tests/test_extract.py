from unittest.mock import MagicMock, patch

import pytest

from ..app.services import extract as extract_module
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# --- extract_action_items_llm (TODO 2): mocked OpenAI, no network ---


@pytest.fixture
def fake_openai_key(monkeypatch):
    monkeypatch.setattr(extract_module, "OPENAI_API_KEY", "sk-test-key-for-ci")


def test_extract_action_items_llm_empty_input():
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   \n\t  ") == []


@patch.object(extract_module, "OpenAI")
def test_extract_action_items_llm_bullet_list(mock_openai_cls, fake_openai_key):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='["Set up database", "Write integration tests"]'))]
    )

    text = """
    - [ ] Set up database
    - Write integration tests
    """.strip()
    items = extract_action_items_llm(text)
    assert items == ["Set up database", "Write integration tests"]
    mock_client.chat.completions.create.assert_called_once()
    call_kw = mock_client.chat.completions.create.call_args[1]
    assert call_kw["temperature"] == 0.2
    assert call_kw["messages"][-1]["content"] == text


@patch.object(extract_module, "OpenAI")
def test_extract_action_items_llm_keyword_prefixed_lines(mock_openai_cls, fake_openai_key):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='["Email the sponsor", "Schedule retro"]'))]
    )

    text = """
    todo: Email the sponsor
    action: Schedule retro
    """.strip()
    items = extract_action_items_llm(text)
    assert items == ["Email the sponsor", "Schedule retro"]


@patch.object(extract_module, "OpenAI")
def test_extract_action_items_llm_fenced_json(mock_openai_cls, fake_openai_key):
    """Model sometimes wraps JSON in markdown fences; parser should still work."""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    fenced = '```json\n["Only task"]\n```'
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=fenced))]
    )

    items = extract_action_items_llm("Anything.")
    assert items == ["Only task"]


def test_extract_action_items_llm_missing_api_key(monkeypatch):
    monkeypatch.setattr(extract_module, "OPENAI_API_KEY", "")
    with pytest.raises(ValueError, match="Missing API key"):
        extract_action_items_llm("some non-empty note body")
