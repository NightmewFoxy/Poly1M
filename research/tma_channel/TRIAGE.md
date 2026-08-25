# TheMovingAverage channel triage (2026-08-25)

Corpus enumerated with yt-dlp:
- **407 main videos** (`channel_videos.txt`) — the analysis corpus.
- **743 shorts** — SKIPPED: sub-60s clips of main-video content; titles are generic
  ("Trade Tips", "Quick Trades", divergence part 1-5 clips); no room for a full
  mechanical rule set that isn't already in a long-form video.
- **34 live streams** — SKIPPED: live trading sessions, not rule teaching; any
  strategy used live is taught in the long-form catalog.

Triage of the 407: keyword pass (strategy/indicator/pattern/entry/SL/TP/session
terms) + manual rescue of filter-type and meta videos (best-time-to-trade,
don't-trade-Monday/December, his trading-bot 3-parter, "I Gave AI 6 Years of
Data", start-to-finish trade walkthroughs) + manual drop of platform tutorials
and price-prediction vlogs. Result: **166 videos** (`final_list.txt`) go to
transcript extraction. Excluded 241: motivation/vlog/prop-firm-news/market
commentary/platform tutorials — no mechanical rules to extract by title; spot
checks confirmed.
