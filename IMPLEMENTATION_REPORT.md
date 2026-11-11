# Boomi Academy — Checkpoint 03

## Added
1. **Appendix A + 16 Certification pages** (were empty except collapsed source text). Content extracted from PDF pp.150-176 with pdfplumber (`tools/extract.py`, `tools/build_supp.py` -> `tools/supp.json`, embedded as `window.__SUPP`). Rendered by `tools/supp.js`: tables (stack on phones), discrepancy cards, callouts, official links, animated step flows (cert02/03/04/07/08/10), 42-question exam with scoring, 8 scenarios, readiness scorecard, checklists, 7/14/30-day plans. State stored in the existing localStorage object. Verbatim source remains the last section.
2. **Exact diagram recreations** (`tools/diag.py`, `tools/diag.js`): 21 regions on pp. 8,10,12,13(x2),38,56,61,75,100,117,119,122,142-149 rebuilt as SVG from the PDF's own rects, Bezier curves, lines and words; step highlight, moving arrow dots (from arrowheads), original crop toggle, large scroll view. Page 8 (cover banner) is stored but not shown (front matter). Embedded as `window.__DIAG`.
3. **Full 176-page audit**: `diagram_audit.json`.

## Verified (real Chromium, 1280/820/390 px)
- 17 supplement pages, 20 diagram-bearing lessons, all 56 lessons + 7 extra tools: no console errors, no horizontal overflow, source text last.
- 20 activities: TUTORIAL shows one image at a time, counts match screenshot_inventory.json, Next works.
- Bookmark, studied, notes, theme, search, revision mode work; quiz/scorecard/reveal/persistence-after-reload work; timers stop on navigation/visibility.
- Pixel diff of recreation vs original crop: `pixel_diff.json`.

## Not verified / limits
See CHECKPOINT_STATUS.json `known_limits`. Notably: Chromium only; no real Android device; 3 s auto-advance not timed; stage order is positional reading order.
