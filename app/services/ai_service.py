import anthropic
import base64
import json
import os
from pathlib import Path
from dataclasses import dataclass


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

SYSTEM_PROMPT = """Sen profesyonel bir trading karar destek asistanısın. Amacın işlem açmak değil, trader'a strateji kurallarına göre analiz sunmaktır.

Görevin:
1. Verilen grafik görüntüsünü analiz et
2. Trader'ın strateji kurallarına göre değerlendir
3. HTF bias çıkar
4. Long ve short senaryoları yaz
5. Kesin kâr vaadi verme
6. Eğer bias net değilse bias değerini "NO_TRADE" olarak ayarla
7. Eğer grafik görüntüsü yetersizse bias değerini "INSUFFICIENT_DATA" olarak ayarla

Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir şey ekleme:

{
  "symbol": "sembol adı",
  "timeframe": "zaman dilimi",
  "bias": "BULLISH | BEARISH | RANGING | NO_TRADE | INSUFFICIENT_DATA",
  "confidence": 1-10 arası tam sayı,
  "market_structure": "piyasa yapısı açıklaması",
  "key_levels": {
    "resistance": ["seviye1", "seviye2"],
    "support": ["seviye1", "seviye2"]
  },
  "summary": "genel piyasa özeti (2-3 cümle)",
  "long_scenario": "long senaryo açıklaması veya N/A",
  "short_scenario": "short senaryo açıklaması veya N/A",
  "no_trade_conditions": ["durum1", "durum2"],
  "risk_notes": "risk notları",
  "telegram_message": "telegram için hazır mesaj metni"
}"""


@dataclass
class AnalysisResult:
    symbol: str
    timeframe: str
    bias: str
    confidence: int
    market_structure: str
    key_levels: dict
    summary: str
    long_scenario: str
    short_scenario: str
    no_trade_conditions: list
    risk_notes: str
    telegram_message: str
    raw_response: str = ""


def _load_knowledge() -> str:
    files = ["strategy.md", "no_trade_conditions.md", "risk_rules.md", "telegram_format.md"]
    content_parts = []
    for fname in files:
        path = KNOWLEDGE_DIR / fname
        if path.exists():
            content_parts.append(f"## {fname}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(content_parts)


def _encode_image(image_bytes: bytes, media_type: str = "image/png") -> tuple[str, str]:
    return base64.standard_b64encode(image_bytes).decode("utf-8"), media_type


def analyze_chart(
    image_bytes: bytes,
    symbol: str,
    timeframe: str,
    manual_note: str = "",
    media_type: str = "image/png",
) -> AnalysisResult:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY bulunamadı. .env dosyasını kontrol et.")

    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    knowledge = _load_knowledge()
    image_data, img_type = _encode_image(image_bytes, media_type)

    user_content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img_type,
                "data": image_data,
            },
        },
        {
            "type": "text",
            "text": f"""Sembol: {symbol}
Zaman Dilimi: {timeframe}
Manuel Not: {manual_note or "Yok"}

---

Strateji ve Kurallar:

{knowledge}

---

Yukarıdaki grafik görüntüsünü ve strateji kurallarını kullanarak analiz yap. Çıktını JSON formatında ver.""",
        },
    ]

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = message.content[0].text.strip()

    # JSON bloğunu temizle
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    data = json.loads(raw)

    return AnalysisResult(
        symbol=data.get("symbol", symbol),
        timeframe=data.get("timeframe", timeframe),
        bias=data.get("bias", "NO_TRADE"),
        confidence=int(data.get("confidence", 0)),
        market_structure=data.get("market_structure", ""),
        key_levels=data.get("key_levels", {"resistance": [], "support": []}),
        summary=data.get("summary", ""),
        long_scenario=data.get("long_scenario", "N/A"),
        short_scenario=data.get("short_scenario", "N/A"),
        no_trade_conditions=data.get("no_trade_conditions", []),
        risk_notes=data.get("risk_notes", ""),
        telegram_message=data.get("telegram_message", ""),
        raw_response=raw,
    )
