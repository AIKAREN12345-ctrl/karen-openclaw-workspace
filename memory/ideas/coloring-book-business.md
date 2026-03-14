# Coloring Book Business Idea

**Status:** Documented for future consideration  
**Date:** 2026-03-11  
**Idea Source:** Ken (user) + Karen (AI assistant)

---

## Why This Idea Resonates

- **Wholesome nature:** Coloring books have a warm, creative, calming feeling behind them
- **Accessible art:** Makes creativity available to everyone, regardless of skill level
- **Therapeutic value:** Known stress-relief and mindfulness benefits
- **Nostalgic + modern:** Classic concept, AI-powered production

---

## The Series Strategy

### Core Concept
Build themed series rather than one-off books. Examples:
- "Cozy Cottages" series
- "Steampunk Animals" series  
- "Underwater Cities" series
- "Fantasy Forests" series
- "Space Exploration" series

### Why Series Work
- **Cross-selling:** "Customers who bought X also bought Y"
- **Brand recognition:** Consistent style builds trust
- **Collectibility:** People want complete sets
- **Marketing efficiency:** Promote one, sell the series

---

## Scale Potential

**The Numbers:**
- 4,000 book series = achievable in days with automation
- Amazon KDP = print-on-demand, zero inventory
- Passive royalties = small per book, volume adds up
- Global reach = Amazon's marketplace

**Production Pipeline:**
1. Curated Midjourney prompts (consistent style)
2. Batch image generation
3. Auto-layout for print (bleed margins, etc.)
4. Metadata + cover design
5. Upload to KDP
6. Rinse and repeat

---

## Expansion Idea: Subscription App for Kids

**Added:** 2026-03-11

### Concept
Digital coloring book subscription app for kids' tablets and iPads:
- **Monthly/annual subscription** vs. one-time purchase
- **Fresh content:** New coloring pages added regularly
- **Interactive features:** Tap-to-fill, gradient tools, stickers
- **Progress tracking:** Badges, completed collections
- **Parent dashboard:** Screen time, activity reports

### Why It Works
- **Recurring revenue** vs. one-time sales
- **No physical inventory** — pure digital
- **Engagement loops:** Kids want new content, parents want peace
- **Platform control:** Not dependent on Amazon's algorithm

### Monetization
- Freemium: Free pages, premium subscription unlocks everything
- $4.99/month or $39.99/year typical kids app pricing
- Family plans for multiple devices

---

## Implementation Details (Full Research)

### Amazon KDP Publishing Requirements

**Trim Sizes:**
- **8.5" x 11"** — Gold standard for coloring books
- **8.5" x 8.5"** — Square format for mandalas
- **6" x 9"** — Pocket/travel size

**Technical Specs:**
- Bleed: 0.125" extension if images go to edge
- Margins: 0.375" inside (gutter) for 24-150 pages
- File: PDF at 300 DPI, grayscale for B&W
- Minimum: 24 pages, Maximum: 828 pages

**Layout Structure:**
- Title page
- Copyright page
- Test page (optional)
- Main coloring pages
- **Blank backing pages** between designs (prevents bleed-through)
- About the author

### AI Image Generation Options

| Option | Cost per 1000 Images | Best For |
|--------|---------------------|----------|
| **Midjourney Official** | ~$173 | Quality, ease of use |
| **Midjourney API** (MidAPI.ai) | ~$93 | Balance of cost/quality |
| **Stable Diffusion Cloud** | ~$23 | Lowest cost, more setup |
| **Stable Diffusion Local** | ~$18 | Full control, requires GPU |

**Midjourney Prompt Formula for Coloring Books:**
```
FOR WHO + CHARACTER + ARTISTIC TECHNIQUES + THINGS NOT INCLUDED
```

**Example Prompt:**
```
coloring page for adults, fantasy dragon, extreme simple line drawing, 
crisp lines, --no shading, color, sketch --ar 3:4
```

**Key Parameters:**
- `--no shading, color, sketch, fill` (removes unwanted elements)
- `--ar 3:4` or `--ar 2:3` for portrait pages
- Consistent aspect ratio throughout book

### Automation Tools

**Image Generation:**
- **Midjourney Automation** (Apify actor) — batch processing
- **MidAPI.ai** — API access without official Midjourney API
- **Stable Diffusion** — Python scripts with diffusers library

**Book Layout:**
- **Canva** — Beginner-friendly, templates available
- **Adobe InDesign** — Professional, master pages
- **Microsoft Word** — Free with KDP templates
- **Kindle Create** — Amazon's free tool

**Specialized Tools:**
- **Nurie Creator** — AI cloud-based, one-time fee
- **Colorin.ai** — Automated generator, multiple sizes

### Cost Breakdown (4,000 Book Series)

**Conservative Estimate:**
- Image generation (Option B - Midjourney API): ~$372 for 4,000 images
- Layout software (Canva Pro): $13/month
- KDP publishing: $0 upfront (print-on-demand)
- **Total startup: ~$400-500**

**Revenue Potential:**
- 4,000 books × $9.99 price × 60% royalty = $23,976 gross
- Minus printing (~$0.75/book) = $20,976 net
- **Break-even: Sell ~50-60 books**

### Production Workflow

1. **Theme Selection** — Pick 5-10 cohesive series
2. **Prompt Development** — Curate 20-30 base prompts per theme
3. **Batch Generation** — 100-200 images per theme
4. **Curation** — Select best 50-100 per book
5. **Layout** — Import to Canva/InDesign with KDP specs
6. **Export** — PDF with bleed, 300 DPI
7. **Cover Design** — Use KDP Cover Calculator
8. **Upload** — KDP dashboard, set pricing
9. **Proof** — Order physical copy to check quality
10. **Publish** — Go live, monitor, iterate

---

## Next Steps (When Ready)

### Phase 1: Research & Validate
- [ ] Check Amazon KDP top-selling coloring book niches
- [ ] Analyze competitor pricing and themes
- [ ] Pick 3-5 series concepts to test

### Phase 2: Prototype
- [ ] Document Midjourney prompts for consistent style
- [ ] Generate 50-100 test images
- [ ] Create first complete book (interior + cover)
- [ ] Order proof copy from KDP

### Phase 3: Scale
- [ ] Build batch generation pipeline
- [ ] Create 10-book mini-series
- [ ] Launch and monitor sales
- [ ] Iterate based on feedback

### Phase 4: Expand
- [ ] Evaluate subscription app opportunity
- [ ] Build digital platform
- [ ] Develop brand and marketing

---

## Why Ken Likes This

> "It has a lovely feeling behind it due to the nature of the idea itself. Also, you can have a consistent passive income."

- Low stress, creative work
- Helps people relax and create
- Scalable without ongoing effort
- Aligns with values of accessibility and joy
- Dual revenue streams (physical + digital)

---

## Resources

**KDP:**
- https://kdp.amazon.com/en_US/help
- Templates: https://kdp.amazon.com/en_US/help/topic/G201834230

**AI Generation:**
- Midjourney: https://www.midjourney.com
- MidAPI: https://docs.midapi.ai
- Stable Diffusion: https://stability.ai

**Tools:**
- Canva: https://www.canva.com
- Adobe InDesign: https://www.adobe.com/products/indesign.html

---

*Full implementation research saved to: memory/research/coloring-book-implementation.md*
