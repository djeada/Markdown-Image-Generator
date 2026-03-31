# Custom CSS Template Examples

Example CSS templates showing how to create your own visual styles for Markdown-Image-Generator.

## How It Works

The Playwright renderer converts your Markdown into HTML, then applies a CSS theme to style it before capturing a screenshot. Each `.css` file controls the entire visual appearance — colors, fonts, spacing, and layout.

## Quick Start

1. **Copy a template** into the themes directory:
   ```bash
   cp templates/examples/minimal_clean.css themes/css/minimal_clean.css
   ```

2. **Use it** with the `--theme` flag:
   ```bash
   python src/main.py input.md --theme minimal_clean
   ```

3. **Customize** — edit the copied file to match your brand or preference.

> **Note:** The `--theme` flag accepts theme *names* (not file paths). Place your `.css` file in `themes/css/` and reference it by filename without the `.css` extension.

## Available Selectors

| Selector | What It Styles |
|---|---|
| `body` | Base font, background color, text color |
| `.slide` | Outer container (fixed dimensions, `overflow: hidden`) |
| `.slide-content` | Inner padding container (default 80px padding) |
| `.slide.title-slide` | Title slides (centered flex layout) |
| `h1.title` | Main title text on title slides |
| `h2` | Section headers |
| `p` | Paragraphs |
| `strong` | Bold text |
| `em` | Italic text |
| `code.inline` | Inline code spans |
| `a` | Links |
| `del` | Strikethrough text |
| `.code-block pre code` | Fenced code blocks (may have `.language-xxx`) |
| `.code-block` | Code block outer wrapper |
| `ul`, `ol`, `li` | Lists |
| `blockquote` | Blockquotes |
| `hr` | Horizontal rules |
| `.table-wrapper table` | Tables |
| `thead`, `tbody`, `th`, `td` | Table parts |
| `.task-list` | Task list container |
| `li.task.checked` / `li.task.unchecked` | Task list items |
| `.checkbox` | Task list checkbox character |
| `.page-number` | Page number badge (`position: absolute`, top-right) |

## Included Templates

| Template | Description |
|---|---|
| `minimal_clean.css` | Ultra-clean, Apple-inspired minimalism — white space and system fonts |
| `instagram_story.css` | Bold sunset gradient optimized for 1080×1920 vertical stories |
| `tech_blog.css` | Dark terminal-inspired theme with green accents |
| `corporate_deck.css` | Professional navy-blue presentation deck |

## Tips for Creating Your Own

- **Start from a template** — copy one of these files and modify it rather than starting from scratch.
- **Style `body` first** — set your background, base font, and text color.
- **Use `'CustomFont'` as the first font-family value** — the renderer injects a custom font under this name when `--font-path` is used.
- **Override list markers** with `ul > li::before` and `ol > li::before` using `list-style: none` and pseudo-elements.
- **The `.slide` container** has fixed dimensions and `overflow: hidden` — design within those bounds.
- **Use `::before` / `::after` on `.slide`** for decorative accents (corners, borders, watermarks).
- **Test with all element types** — use a Markdown file that includes headings, code blocks, tables, lists, blockquotes, and task lists to verify your theme handles everything.
