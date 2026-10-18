# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file.
> If not, strictly follow the rules below.

---

**Project:** CANACO Editorial
**Generated:** 2026-10-18 02:47:38
**Category:** News/Media Platform
**Design Dials:** Variance 4/10 (Balanced / Modern) | Motion 2/10 (Subtle) | Density 5/10 (Standard)

> This system follows `design-system/README.md` as its source of truth. Skill-generated palette suggestions are subordinate to that guide.

---

## Global Rules

### Color Palette

| Role | Hex | CSS Variable |
|------|-----|--------------|
| Primary | `#B45309` | `--color-primary` |
| On Primary | `#FFFFFF` | `--color-on-primary` |
| Primary Hover | `#92400E` | `--color-primary-hover` |
| Primary Soft | `#FEF3C7` | `--color-primary-light` |
| Secondary | `#4D7C0F` | `--color-secondary` |
| Accent/CTA | `#D97706` | `--color-accent` |
| Background | `#FDFBF7` | `--color-bg` |
| Foreground | `#2B2621` | `--color-text` |
| Card | `#FFFFFF` | `--color-card` |
| Muted Surface | `#F5F1EA` | `--color-surface-alt` |
| Muted Foreground | `#6B6259` | `--color-text-muted` |
| Border | `#E7E0D3` | `--color-border` |
| Success | `#4D7C0F` | `--color-success` |
| Warning | `#D97706` | `--color-warning` |
| Destructive | `#B91C1C` | `--color-danger` |
| On Destructive | `#FFFFFF` | `--color-on-destructive` |
| Info | `#0E7490` | `--color-info` |
| Focus Ring | `rgba(217, 119, 6, 0.35)` | `--focus-ring` |

**Color Notes:** Warm terracotta, amber, olive and sand. Avoid cold blue and purple; teal is reserved for neutral information.

### Typography

- **Heading Font:** Crimson Pro
- **Body Font:** Atkinson Hyperlegible
- **Mood:** academic, research, scholarly, accessible, readable
- **Google Fonts:** [Crimson Pro + Atkinson Hyperlegible](https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@400;500;600;700&display=swap)

**CSS Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@400;500;600;700&display=swap');
```

### Spacing Variables

*Density: 5/10 — Standard*

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | `4px` | Tight gaps |
| `--space-2` | `8px` | Icon gaps, inline spacing |
| `--space-3` | `12px` | Compact controls |
| `--space-4` | `16px` | Standard padding |
| `--space-5` | `20px` | Form and card gaps |
| `--space-6` | `24px` | Section padding |
| `--space-8` | `32px` | Large gaps |
| `--space-10` | `40px` | Page group spacing |
| `--space-12` | `48px` | Section margins |
| `--space-16` | `64px` | Hero and page padding |

### Shadow Depths

| Level | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 3px rgba(43,38,33,.06)` | Subtle lift |
| `--shadow-md` | `0 4px 12px rgba(43,38,33,.08)` | Cards, buttons |
| `--shadow-lg` | `0 12px 28px rgba(43,38,33,.12)` | Modals, dropdowns |

---

## Component Specs

### Buttons

```css
/* Primary Button */
.btn-primary {
  background: #B45309;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 200ms ease;
  cursor: pointer;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: #B45309;
  border: 1px solid #B45309;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 200ms ease;
  cursor: pointer;
}
```

### Cards

```css
.card {
  background: #FFFFFF;
  border: 1px solid #E7E0D3;
  border-radius: 10px;
  padding: 24px;
  box-shadow: var(--shadow-md);
  transition: all 200ms ease;
  cursor: pointer;
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
```

### Inputs

```css
.input {
  padding: 10px 12px;
  border: 1px solid #E7E0D3;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 200ms ease;
}

.input:focus {
  border-color: #D97706;
  outline: none;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.35);
}
```

### Modals

```css
.modal-overlay {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow-xl);
  max-width: 500px;
  width: 90%;
}
```

---

## Style Guidelines

**Style:** Minimalism & Swiss Style

**Keywords:** Clean, simple, spacious, functional, white space, high contrast, geometric, sans-serif, grid-based, essential

**Best For:** Enterprise apps, dashboards, documentation sites, SaaS platforms, professional tools

**Key Effects:** Subtle hover (200-250ms), smooth transitions, sharp shadows if any, clear type hierarchy, fast loading

### Page Pattern

**Pattern Name:** Hero-Centric Design

- **Conversion Strategy:** One primary CTA. Let the hero dominate the initial viewport without hiding the next content cue. Use a static hero and non-pulsing CTA when reduced motion is requested; provide video controls. Pause hero media offscreen/hidden and keep the final hero message and CTA static under reduced motion.
- **CTA Placement:** Hero dominant (center/bottom) + Sticky nav CTA
- **Section Order:** Full-bleed Hero (headline + visual) > Single value prop strip > Key benefit or proof > Primary CTA

---

## Motion

**Scroll Reveal** (Subtle) — Trigger: scroll (viewport enter) | Duration: 300-400ms | Easing: `power1.out`

```js
gsap.from(el, { opacity: 0, y: 12, duration: 0.35, ease: 'power1.out', scrollTrigger: { trigger: el, start: 'top 90%', toggleActions: 'play none none reverse' } });
```

**Framework notes:** Requires the ScrollTrigger plugin registered once via gsap.registerPlugin(ScrollTrigger); Use matchMedia('(prefers-reduced-motion: reduce)') to skip non-essential motion and render the final state immediately

- ✅ Keep the y offset small (8-16px) so it reads as a fade, not a slide
- ❌ Don't reveal below-the-fold content needed for SEO/crawlers as invisible-by-default without a no-JS fallback
- ⚡ toggleActions 'play none none reverse' avoids re-triggering on every scroll direction change

---

## Anti-Patterns (Do NOT Use)

- ❌ Cluttered layout
- ❌ Slow loading

### Additional Forbidden Patterns

- ❌ **Emojis as icons** — Use SVG icons (Heroicons, Lucide, Simple Icons)
- ❌ **Missing cursor:pointer** — All clickable elements must have cursor:pointer
- ❌ **Layout-shifting hovers** — Avoid scale transforms that shift layout
- ❌ **Low contrast text** — Maintain 4.5:1 minimum contrast ratio
- ❌ **Instant state changes** — Always use transitions (150-300ms)
- ❌ **Invisible focus states** — Focus states must be visible for a11y

---

## Pre-Delivery Checklist

Before delivering any UI code, verify:

- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150-300ms)
- [ ] Light mode: text contrast 4.5:1 minimum
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375px, 768px, 1024px, 1440px
- [ ] No content hidden behind fixed navbars
- [ ] No horizontal scroll on mobile
