# Copy Everything From the Archive Website

Because the Wayback Machine cannot be opened automatically from this environment, you can copy every page and all background pictures yourself and drop them into this project. Follow these steps.

## 1. Open every page in the archive

In your browser, go to:

- **Home:**  
  https://web.archive.org/web/20171123193547/http://www.scholarvalley.com/

- Then open **every other page** on the site (click every link in the header/footer and sidebar, and note the URLs).  
  Examples of URLs you might see:
  - `.../about` or `.../about.html`
  - `.../services`
  - `.../contact`
  - Any other section (e.g. Testimonials, FAQ)

Open each URL in the archive and keep the tab open (or write down the full archive URL for each page).

## 2. Copy the text and structure

For **each** page:

1. Select all the main content (headings, paragraphs, lists).
2. Copy it (Ctrl+C / Cmd+C).
3. Paste it into the matching file in this project:

   - **Home** → `static/index.html`  
     Replace the content inside `<main>...</main>` (hero text, section titles, service cards, about blurb, contact line). Keep the `<header>`, `<footer>`, and `<script>` tags.

   - **About** → `static/about.html`  
     Replace the placeholder paragraphs inside `<section class="section section-page section-about">...</section>`.

   - **Services** → `static/services.html`  
     Replace the placeholder content in the same way.

   - **Contact** → `static/contact.html`  
     Replace the placeholder content (address, phone, email, form labels if any).

If you have more pages (e.g. Testimonials, FAQ), add a new file like `static/testimonials.html` and a route in `app/main.py` (same pattern as `/about`, `/services`, `/contact`), then paste the content there.

## 3. Save every background picture (and other images)

1. On each archive page, **right‑click** any background or full‑width image.
2. Choose **“Save image as…”** (or “Save picture as…”).
3. Save it into the folder:  
   **`static/assets/`**

Suggested names (you can rename to match):

- **Hero / main banner:**  
  `hero-bg.jpg` or `hero-bg.png`
- **General page background (tiled or full):**  
  `body-bg.png` or `body-bg.jpg`
- **About section:**  
  `about-bg.jpg`
- **Other section or page images:**  
  `services-bg.jpg`, `contact-bg.jpg`, or any name you prefer.

Put **all** images you want on the site into `static/assets/`. The CSS is already set up to use:

- `body-bg.png` – full‑page background (add class `bg-image` to `<body>` in each HTML file if you want it).
- `hero-bg.jpg` – hero section background (add class `bg-image` to the `<section class="hero">` in `static/index.html`).

If you use different filenames, edit `static/styles.css` and change the `url(...)` paths to match (e.g. `url("/static/assets/your-filename.jpg")`).

## 4. Turn on the backgrounds in the HTML

- **Full‑page background:**  
  In each HTML file, change `<body>` to  
  `<body class="bg-image">`  
  (only if you added `body-bg.png` or similar and want it on that page).

- **Hero background (home page):**  
  In `static/index.html`, change  
  `<section id="home" class="hero">`  
  to  
  `<section id="home" class="hero bg-image">`  
  (only if you added `hero-bg.jpg` to `static/assets/`).

## 5. Check links and extra pages

- In the archive, click **every** link and note which ones point to **your** site (not external sites).
- For each internal page, make sure you have a corresponding file under `static/` and a route in `app/main.py` (e.g. `/testimonials` → `testimonials.html`).
- Update navigation in `static/index.html`, `about.html`, `services.html`, and `contact.html` so the menu links match (e.g. `/about`, `/services`, `/contact`). They already do for the four main pages.

## 6. Run the app and confirm

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/  
- http://localhost:8000/about  
- http://localhost:8000/services  
- http://localhost:8000/contact  

Confirm that every page shows the copied text and that background images appear where you added the `bg-image` class and the files in `static/assets/`.

---

## Validate that each page matches the archive

**Automated check against the live archive:** The Wayback Machine cannot be opened from this environment (access forbidden), so there is no way to automatically compare our pages to the live archive URLs.

**What you can do:**

1. **Structure check (no archive needed)**  
   Ensures every page has the required header, nav, main, and footer:

   ```bash
   python3 scripts/validate_archive_pages.py
   ```

2. **Text comparison (after saving the archive)**  
   - In your browser, open each archive page (Home, About, Services, Contact).
   - Use **File → Save As** (or right‑click → “Save as…”) and choose **“Webpage, complete”** or **“Webpage, HTML only”**.
   - Save each into a folder, e.g. `archive/`, with names like `index.html`, `about.html`, `services.html`, `contact.html` (or names that contain those words).
   - Run:

   ```bash
   python3 scripts/validate_archive_pages.py --archive-dir archive
   ```

   The script compares the main text content of each of our pages to the saved archive page and reports overlap (e.g. “~80% = good match”). It does not compare layout or images; use a visual check in the browser for that.

3. **Visual check**  
   Open each of our pages side by side with the archive (e.g. http://localhost:8000/about vs the archive About page) and confirm headings, copy, and images match.

**Summary:** Open every archive page in your browser → copy text into the matching `static/*.html` file → save every background (and other) image into `static/assets/` → add `bg-image` where needed → run `scripts/validate_archive_pages.py` (and optionally `--archive-dir`) → run the app and check each URL visually.
