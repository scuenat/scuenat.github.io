# Social media assets

LinkedIn carousels (PDF document posts, 1080 × 1350 portrait pages), one folder per essay, in English and French. Not part of the website.

Build: `cd <essay>/ && node build.js`. Needs Playwright with Chromium and the Inter and Source Serif 4 fonts installed. Each build writes `carousel-en.pdf`, `carousel-fr.pdf` and preview PNGs, and reports any slide whose content does not fit.
