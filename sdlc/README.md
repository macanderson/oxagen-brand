# The agent SDLC

The page at [sdlc.oxagen.sh](https://sdlc.oxagen.sh) and the template generator behind it. The page shows how Oxagen builds Oxagen with agents at every hour, and it lets a reader make a copy of the process with their company name in it, as a Word file, a PDF, or a Word file to open in Google Docs.

The Vercel project is `oxagen-sdlc` in the `oxagen-inc` team. Its root directory is `sdlc/` in this repository. A push to `main` that changes this folder deploys it.

`sdlc.oxagen.sh` is the main address. The project also answers on `sdlc.oxagen.cloud`, and `vercel.json` sends every request there to the same path on `sdlc.oxagen.sh` with a 308 redirect.

The build also reads the `.vercelignore` at the root of this repository. A root pattern that matches `sdlc/` leaves the build with no files, and every path returns 404. To keep this folder off brand.oxagen.cloud, the deploy step in `.github/workflows/ui.yml` removes `sdlc/` from its own checkout.

## Files

| Path | What it holds |
|---|---|
| `public/index.html` | The page. The logo is inlined from `logo/svg/oxagen-lockup-adaptive.svg`. |
| `public/sdlc.css` | The page styles, on the house palette in `tokens/house-tokens.css`. |
| `public/sdlc.js` | The figures and the form. No dependencies. |
| `public/google-docs.html` | The steps to open the Word file in Google Docs. It starts the download itself. |
| `public/og.png` | The share card. `og/og.html` is its source. |
| `api/template.js` | `GET` or `POST /api/template?company=<name>&format=docx\|pdf\|gdoc`. Returns the file. `gdoc` redirects to `/google-docs`. |
| `api/config.js` | `GET /api/config` returns `{ "gate": true \| false }` for the page. |
| `lib/content.js` | The template text. Both renderers read it. Text in `[[double brackets]]` is a blank. |
| `lib/docx.js`, `lib/pdf.js` | The Word and PDF renderers. |
| `lib/lead.js` | The optional lead gate. |
| `fonts/` | Aeonik at 400, 500, and 700 as static TTF for the PDF, cut from `fonts/aeonik-wght.woff2` with the fontTools instancer. The font library cannot subset a WOFF2 file. |

The form in the oxagen.sh blog post (`apps/web/content/posts/agents-are-waiting-on-a-process-built-for-people` in the oxagen repo) sends a plain `GET` to `/api/template`, so it works without JavaScript.

## The lead gate

The gate is off. To turn it on, set `SDLC_LEAD_GATE=on` in the Vercel project and redeploy. With the gate on:

- The page shows first name, last name, and work email fields, and each is required.
- `/api/template` sends a request without a valid name and email back to the page's form, with the company and format filled in. The blog form lands there too.
- Each lead goes to `https://api.oxagen.sh/v1/cms/leads` with `intent: "demo"` and `source: "sdlc-template"`. That endpoint stores the lead and syncs it to Attio. `SDLC_LEADS_URL` overrides the address.
- A failed lead post is logged and the download still happens.

The gate is a marketing gate, not access control, the same as the ebook gate on oxagen.sh.

## Regenerate

```sh
npm install
npm run og        # public/og.png from og/og.html, with the Playwright install on the machine
npm run samples -- "Acme Robotics" samples   # a sample .docx and .pdf in samples/
```

## The numbers on the page

The merge counts come from GitHub search over `macanderson/oxagen`: pull requests merged from September 1 to 29, 2026, counted by UTC date and bucketed by hour in Pacific time. The query was `repo:macanderson/oxagen is:pr is:merged merged:2026-09-01..2026-09-29`, which returned 1,064. Update the stat cards and `BY_HOUR` in `public/sdlc.js` together.
