"""Render transcript records as a chat-log HTML page with a JSON modal.

Each record is one row in a vertical log: a colored type icon, the record's
text content (plain, escaped, wrapping like a text file), and an eye button
that opens a modal with the full raw JSON. The page is one self-contained
file — inline CSS and JS, no external assets — so it opens from disk or drops
onto a static host.

The renderer is pure: it reads record dicts from :mod:`template_viewer.load`
and never reaches back to disk, so it is trivially testable.

The record types come from the Claude Code SDK session logger:

- ``queue-operation`` — a prompt enqueued for the session (``content`` is the
  prompt text). Rendered as the user's prompt.
- ``user`` — a user turn. Content may be a prompt string or a list of
  ``tool_result`` blocks answering an assistant tool call.
- ``assistant`` — an assistant turn: text, ``tool_use`` calls, ``thinking``.
- ``attachment`` — a capability/tool delta (e.g. ``deferred_tools_delta``).
- ``system`` — a system banner (``init`` and others).
- ``result`` — a final result summary (cost, duration, turns).
- ``atis-latch`` / ``last-prompt`` — internal session markers.
- ``raw`` — a line that failed to parse as JSON, kept visible.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .load import Record

__all__ = ["render_html", "render_transcript", "TYPE_META"]


def render_transcript(path: Path, *, title: str | None = None) -> str:
    """Load and render the transcript at ``path`` into one HTML string."""
    from .load import load_records

    records = load_records(path)
    return render_html(records, title=title or _default_title(path))


def render_html(records: list[Record], *, title: str | None = None) -> str:
    """Render a list of transcript records into a self-contained HTML page."""
    title = title or "Transcript"
    header = _Header.collect(records)
    rows = "\n".join(_render_row(i, r) for i, r in enumerate(records))
    records_json = _embed_json(records)
    return _page(title, header, rows, records_json)


# --------------------------------------------------------------------------- #
# Type metadata: icon + label + css class
# --------------------------------------------------------------------------- #

TYPE_META: dict[str, tuple[str, str]] = {
    "queue-operation": ("📨", "prompt"),
    "user": ("💬", "user"),
    "assistant": ("🤖", "assistant"),
    "attachment": ("📎", "attachment"),
    "system": ("⚙️", "system"),
    "result": ("🏁", "result"),
    "atis-latch": ("🔒", "latch"),
    "last-prompt": ("📌", "last-prompt"),
    "raw": ("❓", "raw"),
}
_DEFAULT_ICON = "•"


def _meta(rtype: str) -> tuple[str, str]:
    return TYPE_META.get(rtype, (_DEFAULT_ICON, rtype))


def _css_class(rtype: str) -> str:
    return rtype.replace("_", "-")


# --------------------------------------------------------------------------- #
# Row rendering
# --------------------------------------------------------------------------- #


def _render_row(index: int, record: Record) -> str:
    rtype = record.get("type", "unknown")
    icon, label = _meta(rtype)
    text = _content_text(record)
    return (
        f'<div class="row type-{_css_class(rtype)}">'
        f'<span class="icon" aria-hidden="true">{icon}</span>'
        f'<span class="kind">{html.escape(label)}</span>'
        f'<span class="content">{html.escape(text)}</span>'
        f'<button class="eye" data-i="{index}" title="View JSON" '
        f'aria-label="View JSON for record {index}">👁</button>'
        f"</div>"
    )


def _content_text(record: Record) -> str:
    rtype = record.get("type")
    if rtype == "queue-operation":
        return _queue_text(record)
    if rtype == "user":
        return _user_text(record.get("message") or {})
    if rtype == "assistant":
        return _assistant_text(record.get("message") or {})
    if rtype == "attachment":
        return _attachment_text(record)
    if rtype == "atis-latch":
        return "session latch"
    if rtype == "last-prompt":
        return record.get("lastPrompt", "")
    if rtype == "result":
        return _result_text(record)
    if rtype == "system":
        return record.get("subtype", "system")
    if rtype == "raw":
        return record.get("line", "")
    # A record type the renderer has never seen. Surfaced, not hidden.
    return _truncate(json.dumps(record, default=str, ensure_ascii=False), 160)


def _queue_text(record: Record) -> str:
    op = record.get("operation", "")
    if op == "enqueue":
        return record.get("content", "") or "[enqueue]"
    return f"[queue: {op}]"


def _user_text(message: dict) -> str:
    blocks = _as_blocks(message.get("content"))
    if not blocks:
        return ""
    # A user turn of pure tool results is a tool-result turn, not a prompt.
    parts: list[str] = []
    for b in blocks:
        bt = b.get("type")
        if bt == "text":
            parts.append(b.get("text", ""))
        elif bt == "tool_result":
            tid = b.get("tool_use_id", "")
            txt = _block_text(b.get("content"))
            tag = "tool result" + (f" {tid}" if tid else "")
            err = " (error)" if b.get("is_error") else ""
            parts.append(f"[{tag}{err}] {_truncate(txt, 300)}")
        else:
            parts.append(f"[{bt}]")
    return "\n".join(parts)


def _assistant_text(message: dict) -> str:
    blocks = _as_blocks(message.get("content"))
    parts: list[str] = []
    for b in blocks:
        bt = b.get("type")
        if bt == "text":
            parts.append(b.get("text", ""))
        elif bt == "tool_use":
            name = b.get("name", "tool")
            parts.append(f"→ {name}: {_one_line(b.get('input', {}))}")
        elif bt == "thinking":
            parts.append(f"(thinking) {b.get('thinking', '')}")
        else:
            parts.append(f"[{bt}]")
    return "\n".join(parts)


def _attachment_text(record: Record) -> str:
    att = record.get("attachment") or {}
    sub = att.get("type", "attachment")
    if sub == "deferred_tools_delta":
        return _delta_line(sub, att, "addedNames", "removedNames")
    if sub == "agent_listing_delta":
        return _delta_line(sub, att, "addedTypes", "removedTypes")
    if sub == "skill_listing":
        count = att.get("skillCount", len(att.get("names") or []))
        return f"skill_listing ({count} skills)"
    if sub == "total_tokens_reminder":
        text = att.get("text", "")
        # Strip the <total_tokens>...</total_tokens> wrapper for the row.
        inner = text.replace("<total_tokens>", "").replace("</total_tokens>", "").strip()
        return inner or sub
    if sub == "edited_text_file":
        fname = att.get("filename", "")
        return f"edited_text_file {fname}" if fname else sub
    if sub == "queued_command":
        mode = att.get("commandMode", "")
        return f"queued_command ({mode})" if mode else sub
    if sub == "read_truncation_notice":
        banner = att.get("banner", "")
        return _truncate(banner, 160) if banner else sub
    if sub == "date_change":
        new = att.get("newDate", "")
        return f"date_change → {new}" if new else sub
    return sub


def _delta_line(sub: str, att: dict, added_key: str, removed_key: str) -> str:
    added = len(att.get(added_key) or [])
    removed = len(att.get(removed_key) or [])
    bits = []
    if added:
        bits.append(f"+{added}")
    if removed:
        bits.append(f"-{removed}")
    suffix = " ".join(bits)
    return f"{sub} {suffix}" if suffix else sub


def _result_text(record: Record) -> str:
    parts: list[str] = []
    subtype = record.get("subtype")
    if subtype:
        parts.append(str(subtype))
    if "total_cost_usd" in record:
        parts.append(f"${record['total_cost_usd']:.4f}")
    if "duration_ms" in record:
        parts.append(f"{record['duration_ms'] / 1000:.1f}s")
    if "num_turns" in record:
        parts.append(f"{record['num_turns']} turns")
    if record.get("is_error"):
        parts.append("error")
    return " · ".join(parts) if parts else "result"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _as_blocks(content: Any) -> list[dict]:
    if content is None:
        return []
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return [{"type": "text", "text": str(content)}]


def _block_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    blocks = _as_blocks(content)
    return "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def _one_line(value: Any) -> str:
    if isinstance(value, (dict, list)):
        s = json.dumps(value, default=str, ensure_ascii=False)
    else:
        s = str(value)
    return _truncate(s.replace("\n", " "), 120)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " …"


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _default_title(path: Path) -> str:
    return f"Transcript · {path.name}"


def _embed_json(records: list[Record]) -> str:
    """Render records as JSON safe to embed inside a <script> block."""
    body = json.dumps(records, default=str, ensure_ascii=False, indent=2)
    # `<` only appears inside JSON string values; escape so a literal
    # `</script>` in model output can never terminate the block early.
    return body.replace("<", "\\u003c")


# --------------------------------------------------------------------------- #
# Header / totals
# --------------------------------------------------------------------------- #


class _Header:
    """Session metadata and rolling usage totals, collected from the records."""

    def __init__(self) -> None:
        self.session_id: str | None = None
        self.cwd: str | None = None
        self.version: str | None = None
        self.git_branch: str | None = None
        self.total_input = 0
        self.total_cache_creation = 0
        self.total_cache_read = 0
        self.total_output = 0
        self.api_calls = 0
        self._seen_message_ids: set[str] = set()

    @classmethod
    def collect(cls, records: Any) -> "_Header":
        h = cls()
        for record in records:
            h.absorb(record)
        return h

    def absorb(self, record: Record) -> None:
        rtype = record.get("type")
        if rtype == "system" and record.get("subtype") == "init":
            self.session_id = record.get("sessionId") or self.session_id
            self.cwd = record.get("cwd") or self.cwd
            self.version = record.get("version") or self.version
            self.git_branch = record.get("gitBranch") or self.git_branch
        elif rtype == "assistant":
            message = record.get("message") or {}
            mid = message.get("id")
            usage = message.get("usage") or {}
            if mid and mid in self._seen_message_ids:
                return
            if mid:
                self._seen_message_ids.add(mid)
            self.total_input += _int(usage.get("input_tokens"))
            self.total_cache_creation += _int(usage.get("cache_creation_input_tokens"))
            self.total_cache_read += _int(usage.get("cache_read_input_tokens"))
            self.total_output += _int(usage.get("output_tokens"))
            self.api_calls += 1

    def as_html(self) -> str:
        meta_rows: list[str] = []
        if self.session_id:
            meta_rows.append(f"<dt>session</dt><dd>{html.escape(self.session_id)}</dd>")
        if self.cwd:
            meta_rows.append(f"<dt>cwd</dt><dd><code>{html.escape(self.cwd)}</code></dd>")
        if self.git_branch:
            meta_rows.append(f"<dt>branch</dt><dd><code>{html.escape(self.git_branch)}</code></dd>")
        if self.version:
            meta_rows.append(f"<dt>version</dt><dd>{html.escape(self.version)}</dd>")
        meta = "<dl>" + "".join(meta_rows) + "</dl>" if meta_rows else ""
        usage = (
            f"<span class='stat'><b>{self.total_input:,}</b> in</span>"
            f"<span class='stat'><b>{self.total_cache_creation:,}</b> cache write</span>"
            f"<span class='stat'><b>{self.total_cache_read:,}</b> cache read</span>"
            f"<span class='stat'><b>{self.total_output:,}</b> out</span>"
            f"<span class='stat'><b>{self.api_calls}</b> calls</span>"
        )
        if not meta and not usage.strip():
            return ""
        return f"<div class='meta'>{meta}</div><div class='usage'>{usage}</div>"


# --------------------------------------------------------------------------- #
# Page shell
# --------------------------------------------------------------------------- #

_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  margin: 0; padding: 0; background: #f6f7f9; color: #1b1f24; font-size: 13px; line-height: 1.5;
}
header.bar {
  position: sticky; top: 0; z-index: 10; background: #ffffff; border-bottom: 1px solid #d0d7de;
  padding: 10px 16px; display: flex; flex-direction: column; gap: 6px;
}
header.bar h1 { margin: 0; font-size: 14px; font-weight: 600; }
header.bar .meta dt { float: left; clear: left; width: 60px; color: #57606a; font-weight: 600; }
header.bar .meta dd { margin: 0 0 2px 68px; }
header.bar .meta dl { margin: 0; }
header.bar .usage { display: flex; flex-wrap: wrap; gap: 12px; }
.stat { font-size: 11px; color: #57606a; }
.stat b { color: #1b1f24; }
main { max-width: 1100px; margin: 0 auto; padding: 12px 16px; }
.row {
  display: grid;
  grid-template-columns: 22px 84px 1fr auto;
  align-items: start; gap: 10px;
  background: #ffffff; border: 1px solid #eaeef2; border-radius: 6px;
  padding: 8px 12px; margin-bottom: 6px;
}
.row:hover { border-color: #d0d7de; }
.row .icon { font-size: 14px; line-height: 1.4; text-align: center; }
.row .kind {
  font-size: 11px; text-transform: uppercase; letter-spacing: .05em;
  color: #57606a; font-weight: 700; padding-top: 1px;
}
.row .content { white-space: pre-wrap; word-break: break-word; min-width: 0; }
.row .eye {
  background: none; border: 1px solid transparent; border-radius: 4px;
  cursor: pointer; font-size: 14px; padding: 0 4px; line-height: 1.4; color: #57606a;
}
.row .eye:hover { background: #eff1f3; border-color: #d0d7de; color: #1b1f24; }
/* type colors */
.type-queue-operation { border-left: 3px solid #2f81f7; }
.type-queue-operation .kind { color: #2f81f7; }
.type-user { border-left: 3px solid #2f81f7; }
.type-user .kind { color: #2f81f7; }
.type-assistant { border-left: 3px solid #8957e5; }
.type-assistant .kind { color: #8957e5; }
.type-attachment { border-left: 3px solid #6e7681; }
.type-attachment .kind { color: #6e7681; }
.type-system { border-left: 3px solid #6e7681; background: #fbfcfd; }
.type-system .kind { color: #6e7681; }
.type-result { border-left: 3px solid #1a7f37; background: #f6fff6; }
.type-result .kind { color: #1a7f37; }
.type-atis-latch { border-left: 3px solid #d0d7de; background: #fbfcfd; }
.type-atis-latch .kind { color: #8c959f; }
.type-last-prompt { border-left: 3px solid #d0d7de; background: #fbfcfd; }
.type-last-prompt .kind { color: #8c959f; }
.type-raw { border-left: 3px solid #cf222e; }
.type-raw .kind { color: #cf222e; }
/* modal */
.modal { position: fixed; inset: 0; z-index: 100; display: flex; align-items: center; justify-content: center; }
.modal.hidden { display: none; }
.modal-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,.5); }
.modal-panel {
  position: relative; background: #ffffff; color: #1b1f24; border-radius: 8px;
  width: min(900px, 92vw); height: min(80vh, 700px); display: flex; flex-direction: column;
  box-shadow: 0 8px 30px rgba(0,0,0,.25); border: 1px solid #d0d7de;
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px; border-bottom: 1px solid #eaeef2; font-size: 12px; color: #57606a;
}
.modal-close {
  background: none; border: none; cursor: pointer; font-size: 16px; color: #57606a; line-height: 1;
}
.modal-close:hover { color: #1b1f24; }
.modal-body { overflow: auto; padding: 12px; }
.modal-body pre {
  margin: 0; white-space: pre-wrap; word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px;
}
.empty { color: #8c959f; padding: 24px; text-align: center; }
@media (prefers-color-scheme: dark) {
  body { background: #0d1117; color: #c9d1d9; }
  header.bar { background: #161b22; border-color: #30363d; }
  .stat b { color: #c9d1d9; }
  .row { background: #161b22; border-color: #21262d; }
  .row:hover { border-color: #30363d; }
  .row .eye { color: #8b949e; }
  .row .eye:hover { background: #21262d; color: #c9d1d9; }
  .type-system, .type-atis-latch, .type-last-prompt { background: #0d1117; }
  .type-result { background: #0d1a0d; }
  .modal-panel { background: #161b22; border-color: #30363d; color: #c9d1d9; }
  .modal-head { border-color: #21262d; color: #8b949e; }
  .modal-close { color: #8b949e; }
}
"""

_JS = """
const RECORDS = JSON.parse(document.getElementById('records').textContent);
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modal-title');
const modalJson = document.getElementById('modal-json');

function showJson(i) {
  modalTitle.textContent = 'record ' + i + ' · ' + (RECORDS[i] && RECORDS[i].type || '?');
  modalJson.textContent = JSON.stringify(RECORDS[i], null, 2);
  modal.classList.remove('hidden');
}
function closeModal() { modal.classList.add('hidden'); }

document.addEventListener('click', (e) => {
  const eye = e.target.closest('.eye');
  if (eye) { showJson(Number(eye.dataset.i)); return; }
  if (e.target.closest('.modal-close') || e.target.classList.contains('modal-backdrop')) {
    closeModal();
  }
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
"""


def _page(title: str, header: _Header, rows: str, records_json: str) -> str:
    body = rows if rows.strip() else '<div class="empty">No transcript records.</div>'
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '<header class="bar">\n'
        f"<h1>{html.escape(title)}</h1>\n"
        f"{header.as_html()}\n"
        "</header>\n"
        "<main>\n"
        f"{body}\n"
        "</main>\n"
        '<script type="application/json" id="records">'
        f"{records_json}"
        "</script>\n"
        '<div id="modal" class="modal hidden">\n'
        '<div class="modal-backdrop"></div>\n'
        '<div class="modal-panel">\n'
        '<div class="modal-head">\n'
        '<span id="modal-title">record</span>\n'
        '<button class="modal-close" aria-label="Close">✕</button>\n'
        "</div>\n"
        '<div class="modal-body"><pre id="modal-json"></pre></div>\n'
        "</div>\n"
        "</div>\n"
        f"<script>{_JS}</script>\n"
        "</body>\n"
        "</html>\n"
    )
