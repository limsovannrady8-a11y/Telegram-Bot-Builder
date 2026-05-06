"""
VoxCPM2 Gradio API client (Gradio 5.x SSE endpoints).

Named endpoint: /generate  (fn_index=2)
Parameters (in order):
  0. text_input                str
  1. control_instruction       str
  2. reference_wav_path_input  FileData | None
  3. use_prompt_text           bool
  4. prompt_text_input         str
  5. cfg_value_input           float  (1.0–3.0, default 2.0)
  6. do_normalize              bool
  7. denoise                   bool
Returns:
  [0] FileData  { path, url, ... }
"""

import asyncio
import json
import logging
import random
import string

import httpx

logger = logging.getLogger(__name__)

GRADIO_BASE = "https://openbmb-voxcpm-demo.hf.space"
QUEUE_JOIN  = f"{GRADIO_BASE}/gradio_api/queue/join"
QUEUE_DATA  = f"{GRADIO_BASE}/gradio_api/queue/data"
UPLOAD_URL  = f"{GRADIO_BASE}/gradio_api/upload"
TIMEOUT     = 120.0
POLL_SECS   = 3.0
MAX_RETRIES = 3


def _session() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


async def _upload_audio(
    client: httpx.AsyncClient,
    file_bytes: bytes,
    filename: str = "ref.ogg",
) -> dict | None:
    """Upload audio bytes to the Gradio space and return a FileData dict."""
    try:
        files = {"files": (filename, file_bytes, "audio/ogg")}
        res = await client.post(UPLOAD_URL, files=files, timeout=30)
        if res.status_code != 200:
            logger.error("Upload failed: HTTP %s — %s", res.status_code, res.text[:200])
            return None
        paths = res.json()
        if not paths:
            return None
        return {
            "path": paths[0],
            "meta": {"_type": "gradio.FileData"},
        }
    except Exception as exc:
        logger.error("Upload error: %s", exc)
        return None


def _extract_audio_url(output: dict | None) -> str | None:
    """Extract audio URL from a process_completed output dict."""
    if not output:
        return None
    data_list = output.get("data") or []
    if not data_list:
        return None
    audio_info = data_list[0]
    if not isinstance(audio_info, dict):
        logger.warning("Unexpected audio_info type: %s — value: %s", type(audio_info), audio_info)
        return None
    url = audio_info.get("url") or ""
    path = audio_info.get("path") or ""
    if not url and path:
        url = f"{GRADIO_BASE}/gradio_api/file={path}"
    return url or None


async def _call_generate(
    client: httpx.AsyncClient,
    text_input: str,
    control_instruction: str = "",
    reference_wav: dict | None = None,
    cfg_value: float = 2.0,
) -> dict:
    """
    Call the /generate endpoint and poll for the result.
    Returns {"audio_url": str} on success or {"error": str} on failure.
    """
    session = _session()

    payload = {
        "data": [
            text_input,
            control_instruction,
            reference_wav,
            False,
            "",
            cfg_value,
            False,
            False,
        ],
        "event_data": None,
        "fn_index": 2,
        "fn_name": "/generate",
        "session_hash": session,
        "trigger_id": None,
        "simple_backend": False,
    }

    try:
        join_res = await client.post(QUEUE_JOIN, json=payload, timeout=30)
        if join_res.status_code != 200:
            return {"error": f"Queue join failed: HTTP {join_res.status_code} — {join_res.text[:200]}"}

        joined = join_res.json()
        logger.info("Queue joined: event_id=%s session=%s", joined.get("event_id"), session)

        data_url = f"{QUEUE_DATA}?session_hash={session}"
        deadline = asyncio.get_event_loop().time() + TIMEOUT

        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(POLL_SECS)
            try:
                data_res = await client.get(data_url, timeout=30)
                for line in data_res.text.splitlines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if not raw:
                        continue
                    try:
                        evt = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    msg = evt.get("msg") or evt.get("event")
                    logger.info("SSE event: %s", msg)

                    if msg == "process_completed":
                        success = evt.get("success", True)
                        output = evt.get("output") or {}
                        logger.info("process_completed output: success=%s data=%s",
                                    success, str(output)[:300])

                        audio_url = _extract_audio_url(output)
                        if audio_url:
                            logger.info("Audio URL: %s", audio_url)
                            return {"audio_url": audio_url}

                        # Surface server-side error if present
                        err_msg = output.get("error") or str(output.get("data", ""))
                        return {"error": f"Generation failed on server: {err_msg[:200] or 'empty output'}"}

                    if msg in ("error", "unexpected_error"):
                        err = evt.get("message") or str(evt)
                        return {"error": f"Server error: {err}"}

            except Exception as poll_err:
                logger.warning("Poll error (will retry): %s", poll_err)
                continue

        return {"error": "Timed out waiting for VoxCPM response (120s)"}

    except Exception as exc:
        logger.error("generate_speech exception: %s", exc)
        return {"error": str(exc)}


async def generate_speech(
    text: str,
    instruction: str = "",
    reference_audio_bytes: bytes | None = None,
    reference_audio_filename: str = "ref.ogg",
    cfg_value: float = 2.0,
) -> dict:
    """
    High-level TTS helper with automatic retry (up to MAX_RETRIES attempts).
    Returns {"audio_url": str} or {"error": str}.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        ref_file_data: dict | None = None

        if reference_audio_bytes:
            ref_file_data = await _upload_audio(
                client, reference_audio_bytes, reference_audio_filename
            )
            if ref_file_data is None:
                return {"error": "Failed to upload reference audio to VoxCPM server"}

        last_error = "Unknown error"
        for attempt in range(1, MAX_RETRIES + 1):
            if attempt > 1:
                logger.info("Retrying generate_speech (attempt %d/%d)…", attempt, MAX_RETRIES)
                await asyncio.sleep(2)
            result = await _call_generate(
                client=client,
                text_input=text,
                control_instruction=instruction,
                reference_wav=ref_file_data,
                cfg_value=cfg_value,
            )
            if result.get("audio_url"):
                return result
            last_error = result.get("error", "Unknown error")
            logger.warning("Attempt %d failed: %s", attempt, last_error)

        return {"error": last_error}
