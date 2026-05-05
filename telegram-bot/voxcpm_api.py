"""
VoxCPM2 Gradio API client (Gradio 4.x / gradio_api endpoints).

Named endpoint: /generate
Parameters (in order):
  0. text_input            str
  1. control_instruction   str
  2. reference_wav_path_input  FileData | None
  3. use_prompt_text       bool
  4. prompt_text_input     str
  5. cfg_value_input       float  (1.0–3.0, default 2.0)
  6. do_normalize          bool
  7. denoise               bool
Returns:
  [0] FileData  { path, url, ... }
"""

import asyncio
import json
import logging
import random
import string
import tempfile
import os

import httpx

logger = logging.getLogger(__name__)

GRADIO_BASE = "https://openbmb-voxcpm-demo.hf.space"
QUEUE_JOIN = f"{GRADIO_BASE}/gradio_api/queue/join"
QUEUE_DATA = f"{GRADIO_BASE}/gradio_api/queue/data"
UPLOAD_URL = f"{GRADIO_BASE}/gradio_api/upload"
TIMEOUT = 120.0
POLL_INTERVAL = 2.0


def _session() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


async def _upload_audio(client: httpx.AsyncClient, file_bytes: bytes, filename: str = "ref.ogg") -> dict | None:
    """Upload audio bytes to the Gradio space and return FileData dict."""
    try:
        files = {"files": (filename, file_bytes, "audio/ogg")}
        res = await client.post(UPLOAD_URL, files=files, timeout=30)
        if res.status_code != 200:
            logger.error("Upload failed: %s %s", res.status_code, res.text[:200])
            return None
        paths = res.json()
        if not paths:
            return None
        path = paths[0]
        return {
            "path": path,
            "meta": {"_type": "gradio.FileData"},
        }
    except Exception as exc:
        logger.error("Upload error: %s", exc)
        return None


async def _call_generate(
    client: httpx.AsyncClient,
    text_input: str,
    control_instruction: str = "",
    reference_wav: dict | None = None,
    use_prompt_text: bool = False,
    prompt_text_input: str = "",
    cfg_value: float = 2.0,
) -> dict:
    """
    Call /generate on the VoxCPM Gradio space.
    Returns {"audio_url": str} on success or {"error": str} on failure.
    """
    session = _session()

    payload = {
        "data": [
            text_input,
            control_instruction,
            reference_wav,
            use_prompt_text,
            prompt_text_input,
            cfg_value,
            False,
            False,
        ],
        "event_data": None,
        "fn_index": None,
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
        event_id = joined.get("event_id")
        if not event_id:
            return {"error": f"No event_id in response: {joined}"}

        data_url = f"{QUEUE_DATA}?session_hash={event_id}"
        deadline = asyncio.get_event_loop().time() + TIMEOUT

        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(POLL_INTERVAL)
            try:
                data_res = await client.get(data_url, timeout=20)
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

                    evt_type = evt.get("event") or evt.get("msg")

                    if evt_type in ("complete", "success"):
                        output = evt.get("output") or {}
                        data_list = output.get("data") or evt.get("data") or []
                        if data_list:
                            audio_info = data_list[0]
                            if isinstance(audio_info, dict):
                                url = audio_info.get("url")
                                path = audio_info.get("path", "")
                                if not url and path:
                                    url = f"{GRADIO_BASE}/gradio_api/file={path}"
                                if url:
                                    return {"audio_url": url}
                        return {"error": "Generation returned empty audio data"}

                    if evt_type == "error":
                        msg = evt.get("message") or evt.get("output", {}).get("error", "Unknown error")
                        return {"error": f"Gradio error: {msg}"}

            except Exception as poll_err:
                logger.warning("Poll error (will retry): %s", poll_err)
                continue

        return {"error": "Timed out waiting for VoxCPM response (120s)"}

    except Exception as exc:
        logger.error("generate_speech error: %s", exc)
        return {"error": str(exc)}


async def generate_speech(
    text: str,
    instruction: str = "",
    reference_audio_bytes: bytes | None = None,
    reference_audio_filename: str = "ref.ogg",
    cfg_value: float = 2.0,
) -> dict:
    """
    High-level TTS call. Accepts optional raw audio bytes for voice cloning.
    Returns {"audio_url": str} or {"error": str}.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        ref_file_data: dict | None = None

        if reference_audio_bytes:
            ref_file_data = await _upload_audio(client, reference_audio_bytes, reference_audio_filename)
            if ref_file_data is None:
                return {"error": "Failed to upload reference audio to VoxCPM server"}

        return await _call_generate(
            client=client,
            text_input=text,
            control_instruction=instruction,
            reference_wav=ref_file_data,
            cfg_value=cfg_value,
        )
