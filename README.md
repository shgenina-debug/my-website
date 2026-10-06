# ORITEC: Integrated Engineering Services

Corporate website for ORITEC (أوريتك للخدمات الهندسية المتكاملة). Static HTML, CSS and JavaScript with no build step and no runtime dependencies.

## Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Any static host works (Netlify, Vercel, GitHub Pages, S3, Nginx).

## Structure

```
index.html            All sections, SEO meta, Open Graph, schema.org Organization
assets/css/style.css  Design tokens (top of file), layout, components, motion
assets/js/main.js     Header states, mobile menu, reveals, counters, scroll-linked motion,
                      service traces, project image swap, form validation
assets/img/*.svg      Engineering-drawing artwork used as image placeholders
```

## Design reference

The layout and motion follow the supplied reference video (Outcrowd's Resq.io concept). Each reference section was rebuilt for ORITEC:

| Reference | ORITEC |
| --- | --- |
| Floating pill navigation | Same, turns solid with blur on scroll; full-width sheet on mobile |
| Hero with tilted product dashboard and diagonal light beam | ORITEC station monitoring console that straightens as you scroll |
| Client logo strip | Engineering disciplines strip |
| "Issues arise every day" gradient card with node graph | About card with discipline graph, then animated stats |
| Nodes flowing into a glowing "AI" chip | Eight services wired into an "Integrated engineering" core |
| "All-in-one platform" bento grid | Featured solutions bento |
| Tilted "solid foundation" tiles | "Why ORITEC?" tiles that settle as you scroll |
| "Book your demo" light-beam CTA | "Have an engineering project?" CTA |

Sections not in the reference (industries, projects, process, contact) use the same visual language: pinned horizontal scroll for industries, a sticky image that swaps per project, and a process line that fills as you scroll.

All motion respects `prefers-reduced-motion`.

## Before launch: replace placeholder content

- **Photography.** The `assets/img/*.svg` drawings stand in for real photos. To replace one, drop a photo (WebP or JPEG, about 1600px wide) into `assets/img/` and update the `src` and `alt` in `index.html`. Keep the `width`/`height` attributes at the photo's real ratio.
- **Projects.** The six projects in `#projects` are samples. Replace them with real project names, locations and scopes.
- **Contact details.** `info@oritec.sa`, `+966 50 000 0000` and the WhatsApp link are placeholders. They appear in the contact section, footer, JSON-LD block and `assets/js/main.js` (the `mailto:` address).
- **Domain.** `https://www.oritec.sa/` is used in the canonical, Open Graph and JSON-LD tags.
- **Social links.** LinkedIn and Instagram links point at the platform home pages.
- **OG image.** Add `assets/img/og-image.png` (1200×630).
- **Contact form.** There is no backend yet. On submit the form validates the fields, then opens the visitor's email app with the request filled in. To post to a backend instead (Formspree, a serverless function, a CRM), change the submit handler at the bottom of `main.js`.
