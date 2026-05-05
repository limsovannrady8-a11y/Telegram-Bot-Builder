import asyncio
import json
import random
import string
import logging
import httpx

logger = logging.getLogger(__name__)

GRADIO_BASE = "https://openbmb-voxcpm-demo.hf.space"


def _session_hash() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


async def generate_speech(
    text: str,
    instruction: str = "",
    reference_audio_url: str | None = None,
    reference_text: str = "",
    timeout: float = 90.0,
) -> dict:
    """
    Call the VoxCPM HuggingFace Spaces Gradio API.
    Returns dict with 'audio_url' on success or 'error' on failure.
    """
    session = _session_hash()
    payload = {
        "fn_index": 0,
        "data": [text, instruction, reference_audio_url, reference_text, False],
        "session_hash": session,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            join_res = await client.post(
                f"{GRADIO_BASE}/queue/join",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if join_res.status_code != 200:
                return {"error": f"Queue join failed: HTTP {join_res.status_code}"}

            joined = join_res.json()
            event_id = joined.get("event_id")
            if not event_id:
                return {"error": "No event_id returned from Gradio"}

            data_url = f"{GRADIO_BASE}/queue/data?session_hash={event_id}"

            deadline = asyncio.get_event_loop().time() + timeout
            while asyncio.get_event_loop().time() < deadline:
                await asyncio.sleep(2)
                try:
                    data_res = await client.get(data_url)
                    text_body = data_res.text
                    for line in text_body.splitlines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            evt = json.loads(line[5:])
                        except json.JSONDecodeError:
                            continue
                        if evt.get("event") == "complete" or evt.get("output"):
                            output = evt.get("output") or {}
                            data_list = output.get("data") or evt.get("data") or []
                            if data_list:
                                audio_info = data_list[0]
                                if isinstance(audio_info, dict):
                                    url = audio_info.get("url") or f"{GRADIO_BASE}/file={audio_info.get('name', '')}"
                                    return {"audio_url": url}
                            return {"error": "Empty audio data returned"}
                        if evt.get("event") == "error":
                            return {"error": "Gradio returned an error event"}
                except Exception as poll_err:
                    logger.warning("Poll error: %s", poll_err)
                    continue

            return {"error": "Timed out waiting for VoxCPM response"}

    except Exception as exc:
        logger.error("VoxCPM API error: %s", exc)
        return {"error": str(exc)}
