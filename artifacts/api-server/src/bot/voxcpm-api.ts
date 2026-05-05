const GRADIO_BASE = "https://openbmb-voxcpm-demo.hf.space";

interface GradioEvent {
  event?: string;
  data?: unknown;
  output?: { data?: unknown[] };
}

async function callGradio(
  fnIndex: number,
  data: unknown[],
): Promise<unknown[]> {
  const queueRes = await fetch(`${GRADIO_BASE}/queue/join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fn_index: fnIndex, data, session_hash: Math.random().toString(36).slice(2) }),
  });

  if (!queueRes.ok) {
    throw new Error(`Gradio queue join failed: ${queueRes.status}`);
  }

  const joined = (await queueRes.json()) as { event_id?: string };
  const eventId = joined.event_id;
  if (!eventId) throw new Error("No event_id returned from Gradio");

  return new Promise((resolve, reject) => {
    const evtUrl = `${GRADIO_BASE}/queue/data?session_hash=${eventId}`;
    let resolved = false;

    const timeout = setTimeout(() => {
      if (!resolved) reject(new Error("Gradio timeout after 60s"));
    }, 60_000);

    function poll() {
      fetch(evtUrl)
        .then((r) => r.text())
        .then((text) => {
          const lines = text.split("\n").filter((l) => l.startsWith("data:"));
          for (const line of lines) {
            try {
              const evt = JSON.parse(line.slice(5)) as GradioEvent;
              if (evt.event === "complete" || evt.output) {
                const output = evt.output as { data?: unknown[] } | undefined;
                const result = output?.data ?? (evt.data as unknown[]) ?? [];
                resolved = true;
                clearTimeout(timeout);
                resolve(result);
                return;
              }
              if (evt.event === "error") {
                resolved = true;
                clearTimeout(timeout);
                reject(new Error("Gradio returned error event"));
                return;
              }
            } catch {}
          }
          if (!resolved) setTimeout(poll, 2000);
        })
        .catch((err) => {
          if (!resolved) {
            resolved = true;
            clearTimeout(timeout);
            reject(err);
          }
        });
    }

    setTimeout(poll, 1500);
  });
}

export interface TtsOptions {
  text: string;
  instruction?: string;
  referenceAudioUrl?: string;
  referenceText?: string;
}

export interface TtsResult {
  audioUrl?: string;
  audioBase64?: string;
  mimeType?: string;
  error?: string;
}

export async function generateSpeech(opts: TtsOptions): Promise<TtsResult> {
  try {
    const data = [
      opts.text,
      opts.instruction ?? "",
      opts.referenceAudioUrl ?? null,
      opts.referenceText ?? "",
      false,
    ];

    const result = await callGradio(0, data);
    const audioInfo = result[0] as { url?: string; name?: string } | null;
    if (!audioInfo) return { error: "No audio returned" };

    const audioUrl = audioInfo.url ?? `${GRADIO_BASE}/file=${audioInfo.name}`;
    return { audioUrl };
  } catch (err) {
    return { error: err instanceof Error ? err.message : String(err) };
  }
}
