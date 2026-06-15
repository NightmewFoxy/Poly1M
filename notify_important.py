"""Send a message to the owner's IMPORTANT-only Telegram bot.

Per the global standing instruction (@NightmewFoxyImportantShitbot): errors that
need the owner, money/system alerts, completed deliverables he must see. Creds
come from env: TELEGRAM_IMPORTANT_BOT_TOKEN / TELEGRAM_IMPORTANT_CHAT_ID
(owner chat id 960749908). trust_env=False so a stale proxy can't break it.

Usage:
  python notify_important.py "message text"
  echo "message text" | python notify_important.py
"""
import os
import sys

import httpx


def send(text: str) -> int:
    tok = os.environ.get("TELEGRAM_IMPORTANT_BOT_TOKEN")
    cid = os.environ.get("TELEGRAM_IMPORTANT_CHAT_ID", "960749908")
    if not tok:
        print("TELEGRAM_IMPORTANT_BOT_TOKEN not set in env", file=sys.stderr)
        return 1
    r = httpx.Client(trust_env=False, timeout=15).post(
        f"https://api.telegram.org/bot{tok}/sendMessage",
        json={"chat_id": cid, "text": text[:4000],
              "disable_web_page_preview": True},
    )
    print("telegram", r.status_code, r.text[:160])
    return 0 if r.status_code == 200 else 2


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    sys.exit(send(msg.strip()))
