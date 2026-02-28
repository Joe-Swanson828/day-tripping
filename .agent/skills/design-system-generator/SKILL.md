---
name: design-system-generator
description: Generate and maintain a persistent design system for any app or website project. Use this skill whenever the user wants to establish a visual identity, define a design language, create a theme or style guide, set up design tokens, or ensure visual consistency across their app. Also trigger when the user mentions their app looks "bland", "generic", "like AI slop", or wants to make it look distinctive, unique, or match a specific aesthetic (retro, psychedelic, brutalist, luxury, etc.). Works for React Native, React, HTML/CSS, SwiftUI, Flutter, or any frontend framework.
---

# Design System Generator

Create a complete, persistent design system that an AI coding agent can load and follow to produce visually consistent, distinctive UI across an entire project. The output is a portable `design-system.md` file that lives in the project root and acts as the single source of truth for all visual decisions.

## Why This Exists

AI coding agents default to generic, forgettable aesthetics — Inter font, purple gradients, rounded cards, safe spacing. This skill solves that by capturing a project's unique visual identity upfront and encoding it as a structured document the agent references on every session.

## Workflow Overview

```
Interview → Generate → Review → Save → (Optional: Iterate)
```

1. **Interview** the user about their vision (5-8 targeted questions)
2. **Generate** a complete design system document
3. **Review** with the user, refine based on feedback
4. **Save** as `design-system.md` in the project directory
5. **Iterate** — the system can be updated anytime

---

## Phase 1: Design Interview

Ask questions conversationally, not as a rigid form. Adapt based on what the user shares. The goal is to extract enough information to make bold, specific design choices — not to get vague preferences.

### Core Questions (ask all)

1. **Project & Audience**: "What's the app/site? Who's it for?"
2. **Emotional Target**: "Pick 3 words for how the UI should *feel* when someone uses it." (Offer examples: electric, calm, playful, mysterious, bold, warm, clinical, rebellious, dreamy, sharp, organic, futuristic)
3. **Visual References**: "Name 1-3 apps, websites, album covers, art movements, films, or physical objects whose look you admire — even loosely."
4. **Anti-References**: "What should it absolutely NOT look like? What do you hate in UI?"
5. **Theme Mode**: "Dark, light, or both? Any preference for which is primary?"

### Situational Questions (ask as needed)

6. **Color Anchors**: "Do you have any existing brand colors, or colors you feel strongly about?"
7. **Content Density**: "Is this information-dense (dashboards, data) or spacious (marketing, editorial)?"
8. **Platform**: "What framework/platform? (React Native, React + Tailwind, plain HTML/CSS, SwiftUI, etc.)"
9. **Typography Character**: "Any vibe for text? (clean & geometric, handwritten warmth, typewriter grit, editorial elegance, techy monospace)"
10. **Motion & Interaction**: "How animated should it feel? (subtle & smooth, bold & dramatic, minimal/none)"

### Interview Rules

- If the user gives rich answers, skip redundant questions
- If the user says "just make it look good" or gives vague input, make BOLD choices yourself and present them for approval — don't ask more questions
- If the user provides a screenshot or reference image, extract the implied design language from it
- Never ask more than 8 questions total

---

## Phase 2: Generate the Design System

Based on interview answers, generate the complete `design-system.md` file. Every section must contain SPECIFIC values — no placeholders, no "choose one of these", no vague guidance.

### Document Structure

Use the template in `references/design-system-template.md` as the structural foundation. Fill every section with concrete values derived from the interview.

### Generation Rules

**Be Opinionated**: Make decisive choices. "Primary: #FF6B35" not "choose a warm orange". Every token must be a real, usable value.

**Be Cohesive**: Every choice should reinforce the emotional target. If the vibe is "psychedelic 1960s", the typography, colors, spacing, motion, and component patterns should ALL reflect that — not just the colors.

**Avoid AI Defaults**: Never output these unless explicitly requested:
- Fonts: Inter, Roboto, Open Sans, Arial, system-ui defaults
- Colors: Purple-to-blue gradients, #6366F1, generic teal/coral combos
- Spacing: 8px base with no personality
- Radius: 8px everywhere
- Shadows: Generic box-shadow: 0 2px 4px rgba(0,0,0,0.1)

**Typography Selection**: Choose fonts available from Google Fonts (for web) or system + bundled fonts (for native). Always specify:
- Display/heading font (the personality carrier)
- Body font (readable but characterful)
- Optional: accent/mono font for special elements
- Exact weights to load
- Letter-spacing and line-height values

**Color System**: Define a complete, functional palette:
- 1 Primary color + 2-3 shades (lighter/darker)
- 1 Secondary/accent color + shades
- Background colors (surface hierarchy: base → elevated → overlay)
- Text colors (primary → secondary → muted → disabled)
- Semantic colors (success, warning, error, info)
- All colors must pass WCAG AA contrast on their intended background

**Spacing & Layout**: Define a spacing scale and layout conventions:
- Base unit and scale (e.g., 4px: 4, 8, 12, 16, 24, 32, 48, 64)
- Component internal padding conventions
- Page/screen margins
- Section spacing rhythm

**Component Patterns**: Define the look of core UI primitives:
- Buttons (primary, secondary, ghost — sizes, radius, padding)
- Cards/containers (border, shadow, radius, padding)
- Inputs/forms (border style, focus state, label placement)
- Navigation patterns
- Any project-specific components

**Motion & Interaction**: Define animation tokens:
- Duration scale (fast: 150ms, normal: 250ms, slow: 400ms)
- Easing curves
- Transition properties for interactive elements
- Page/screen transition style
- Hover/press state conventions

---

## Phase 3: Review & Refine

Present the generated design system to the user. Highlight the key decisions:
- "Here's the direction I went — [aesthetic name/description]"
- Show the color palette visually if possible (HTML color swatches)
- Call out the font choices and why
- Note any bold or unusual decisions

Ask: "Does this capture what you're going for? Anything to adjust?"

If feedback is given, update the system and re-present. Repeat until approved.

---

## Phase 4: Save & Integrate

Save the approved design system as `design-system.md` in the project root (or user-specified location).

Tell the user:
- "Your design system is saved at `[path]/design-system.md`"
- "Any AI coding agent that reads this file will follow these visual standards"
- "You can reference it in your CLAUDE.md or project instructions with: `Read design-system.md before building any UI components`"
- "To update it later, just ask me to revise the design system"

---

## Phase 5 (Optional): Generate Preview

If the user wants to see the system in action, generate a single-page HTML preview that demonstrates:
- Typography hierarchy (h1-h4, body, caption, mono)
- Color palette swatches with hex codes
- Button variants
- A sample card component
- Spacing/layout examples

This preview acts as a living style guide the user can open in a browser.

---

## Updating an Existing Design System

If a `design-system.md` already exists in the project:
1. Read it first
2. Ask what the user wants to change
3. Make targeted updates while preserving the rest
4. Show the diff of changes
5. Save the updated version

---

## Framework-Specific Output Notes

When generating the design system, include a section with framework-specific implementation guidance:

- **React + Tailwind**: Express tokens as tailwind.config.js extensions + CSS variables
- **React Native**: Express tokens as a StyleSheet-compatible theme object
- **HTML/CSS**: Express tokens as CSS custom properties on :root
- **SwiftUI**: Express tokens as a Theme struct with static properties
- **Flutter**: Express tokens as a ThemeData configuration

Always include the raw values AND the framework-specific format.
