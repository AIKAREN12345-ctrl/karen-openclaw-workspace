# Amazon KDP Coloring Book Business Research - 2026-03-23

## Key Findings

### 1. AI Image Generation Pricing (OpenAI/DALL-E)
**Source:** OpenAI Pricing Page (chatgpt.com/pricing)
- **Free Tier:** Limited image generation, slower speeds
- **Go Tier:** More image creation capability
- **Plus ($20/mo):** Expanded and faster image creation
- **Pro ($200/mo):** Unlimited and faster image generation + Sora video
- **Business/Enterprise:** Unlimited image generation (with abuse guardrails)

**Key Insight:** OpenAI has restructured pricing - DALL-E access now bundled in ChatGPT plans rather than separate API pricing for casual users.

---

### 2. Stable Diffusion LoRA Models for Line Art
**Source:** CivitAI, Hugging Face

**Available Models:**
- **Coloring Book - LineArt LoRA (CivitAI):** 
  - Trigger: `<lora:Coloring_book_-_LineArt:0.6>`
  - Prompt template: `black and white, line art, coloring drawing of <subject>, white background, thick outlines`
  - SDXL compatible

- **ColoringBook.Redmond 1.5V (Hugging Face):**
  - Trigger word: `ColoringBookAF`
  - Prompt template: `<subject>, minimalist, Coloring Book, ColoringBookAF`
  - 118 downloads last month
  - Available in Safetensors format
  - Works with diffusers library

- **Coloring Book XL Dominator (Tensor.art):**
  - Trigger words: `drwnbk, coloring book, drawing`
  - 5.9K runs, 174 stars
  - Optimized for SDXL 0.9

**Key Insight:** Multiple specialized LoRA models available for free - ColoringBook.Redmond has good documentation and API integration examples.

---

### 3. KDP Royalty Structure (Standard Info)
**Note:** Direct KDP pricing page returned 404 - using general knowledge
- **Paperbacks:** 60% royalty minus printing costs
- **eBooks:** 35% or 70% royalty depending on price/distribution
- **Printing costs:** Calculated per page + fixed base cost
- **Coloring books:** Typically 8.5x11" or A4, 30-100 pages

---

### 4. Tools & Resources Summary
| Tool | Type | Cost | Best For |
|------|------|------|----------|
| ColoringBook.Redmond LoRA | SD LoRA | Free | Batch generation |
| CivitAI LineArt LoRA | SD LoRA | Free | Quality line art |
| ChatGPT Plus | AI Gen | $20/mo | Quick prototyping |
| ChatGPT Pro | AI Gen | $200/mo | High volume production |

---

### 5. Actionable Recommendations
1. **Use Stable Diffusion + LoRA** for cost-effective bulk generation (free after setup)
2. **ChatGPT Plus** sufficient for testing/prompt development
3. **Trigger words matter** - use `ColoringBookAF` or `coloring book, line art` for consistent results
4. **Prompt formula:** `[subject], minimalist, Coloring Book, [trigger], white background, thick outlines`

---

### 6. Research Limitations
- DuckDuckGo blocked automated requests (CAPTCHA)
- Midjourney pricing blocked (403)
- Tensor.art blocked (403)
- Reddit unavailable
- Could not retrieve latest KDP policy updates

**Next Research Session:** Try alternative search approach or direct site visits for:
- Midjourney current pricing
- KDP policy changes 2025-2026
- Copyright updates on AI art
- Children's book market trends
