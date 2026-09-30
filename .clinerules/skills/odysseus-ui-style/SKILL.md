---
name: odysseus-ui-style
description: Visual/UI change requirements for Odysseus — matching the existing visual language, CSS variables, and the screenshot requirement for any rendering change.
---

# Odysseus UI / Visual Change Rules

Applies to anything that changes what the app looks like: buttons, icons, fonts, colors, spacing, layout, CSS, HTML, SVG, or any `static/js/` module that draws to the DOM. PRs that change rendering without following these WILL be closed.

## Before submitting a UI change
1. **Run the app locally** and view the change in a browser — type-checks and unit tests are not enough.
2. **Attach a screenshot or short clip** of the running app. Add a mobile screenshot too if it affects mobile.
3. **Match the existing visual language:**
   - Reuse existing CSS variables (`--red`, `--fg`, `--bg`, `--card`, `--border`, …). Do **not** introduce new color values, font sizes, or spacing units.
   - Reuse existing button, input, card, and border classes. Don't invent parallel styling for similar widgets.
   - **No Unicode emoji in UI or code.** Inline SVG matching the monochrome icon style in `static/index.html`, or plain text.
   - Monospaced font (Fira Code) for primary UI text — don't override.
   - Dark theme is default; light-mode work must go through the existing theme system.
4. **No new component patterns** — if a similar widget exists, extend it instead of writing a parallel one.
