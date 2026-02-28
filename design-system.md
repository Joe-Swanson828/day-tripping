# Design System: Day Tripping

## 1. Brand Vision & Identity
- **Theme**: Psychedelic Western meeting Ralph Steadman's visceral ink art.
- **Emotional Target**: Uncanny, Unsettling, Dreamy.
- **Visual Style**: Dark void-like backgrounds, burning sun colors (reds, yellows, oranges), wobbly/sketchy borders, and harsh contrasting shadows.

## 2. Color System
Core palette built for a dark mode environment.

### Backgrounds (The Void)
- **Base Background**: `#080010` (Abyssal Purple)
- **Elevated Surface 1**: `#140524` (Deep Space Violet)
- **Elevated Surface 2**: `#22093B` (Bruise Purple)

### Brand Colors (The Sun)
- **Primary**: `#FF2A00` (Steadman Blood Red)
- **Secondary**: `#FF8100` (Peyote Orange)
- **Accent**: `#EAEF00` (Acid Sun Yellow)

### The Landscape (Wavy & Organic)
- **Motifs**: Flowing, concentric waves of color (like the sunset/radiating lines in the references). 
- **Application**: Subtle background gradients, repeating CSS radial patterns, or large, organic vector shapes behind the main UI.

### The Inhabitants (Creatures & Figures)
- **Vibe**: Distorted, elongated, and highly stylized. Not exactly Steadman (less ink-splatter, more coherent but bizarre shapes).
- **Subjects**: melting cacti, many-eyed coyotes, stretched-out cowboys, and uncanny starry skies.
- **Application**: These should emerge from the "pure black/void" areas of the app, either as subtle low-opacity background images or as distinct floating elements on empty states.

### Text
- **Primary Text**: `#F1EADD` (Bleached Bone)
- **Secondary Text**: `#A88E96` (Dried Blood/Mauve)
- **Muted Text**: `#5E4057`

### Semantic Colors
- **Success/Tripping**: `#00FF88` (Neon Toxic Green)
- **Warning**: `#FFD500`
- **Error**: `#FF003C`

## 3. Typography
Juxtaposing chaotic, sketchy headings with rigid, uncanny monospace body text.

- **Headings / Display**: `Fredericka the Great` (Google Fonts)
  - Vibe: Sketchy, visceral, slightly deranged (evoking Steadman).
  - Weights: 400
  - Usage: App titles, major section headers.
- **Body Text**: `Space Mono` (Google Fonts)
  - Vibe: Clinical, slightly robotic, retro-tech.
  - Weights: 400, 700
  - Usage: Labels, paragraphs, data readout.
- **Alternative Heading (Native/Fallback)**: `Courier New` or a system Serif in bold/italic.

## 4. Spacing & Layout
A slightly uncomfortable, dense spacing scale.

- **Base Unit**: `4px`
- **Scale**: `4px, 8px, 12px, 20px, 32px, 52px` (Slightly unpredictable fibonacci-esque scaling)
- **Borders**: Uneven, wobbly. Use CSS `border-radius: 255px 15px 225px 15px/15px 225px 15px 255px` to simulate hand-drawn boxes.

## 5. Component Patterns

### Buttons
- **Primary Button**:
  - Background: `#FF2A00`
  - Text: `#F1EADD`
  - Border: 2px solid `#EAEF00`
  - Border-Radius: Wobbly/Organic
  - Shadow: Hard offset `4px 4px 0px #EAEF00` (No blur)
- **Secondary / Ghost Button**:
  - Background: Transparent
  - Border: 2px dashed `#FF8100`
  - Text: `#FF8100`

### Cards
- **Background**: `#140524`
- **Border**: 1px solid `#FF2A00`
- **Shadow**: `-4px 4px 0px #5E4057`
- **Corners**: Sharp or slightly wobbly. No perfect 8px curves.

## 6. Motion & Interaction
Unsettling, snappy, and jittery.
- **Duration**: `100ms` (Too fast, uncanny) to `600ms` (Dreamy, too slow). Avoid the comforting `250ms`.
- **Easing**: `cubic-bezier(0.1, -0.6, 0.2, 0)` (Bounces back uncomfortably).
- **Hover States**: Invert colors, or shift shadows drastically instead of fading.

## 7. Imagery & Assets
The app should utilize custom-generated graphics to fill the void spaces.
- **Style**: Saturated colors, thick outlines, concentric radiation (like a heatwave), and surreal proportions.
- **Backgrounds**: Deep black space filled with swirling, psychedelic starscapes or melting desert landscapes.

## 7. Implementation Tokens

### CustomTkinter (Python)
```python
# themes.py integration
"color": {
    "window_bg_color": ["#F1EADD", "#080010"],
    "fg_color": ["#D9D0C1", "#140524"],
    "top_fg_color": ["#C2B5A5", "#22093B"],
    "button_color": ["#FF2A00", "#FF2A00"],
    "button_hover_color": ["#EAEF00", "#EAEF00"],
    "text_color": ["#080010", "#F1EADD"],
    "text_color_disabled": ["#A88E96", "#5E4057"]
}
```

### CSS Variables (map.html)
```css
:root {
  --bg-void: #080010;
  --bg-surface: #140524;
  --bg-elevated: #22093B;

  --color-primary: #FF2A00;
  --color-secondary: #FF8100;
  --color-accent: #EAEF00;

  --text-primary: #F1EADD;
  --text-secondary: #A88E96;

  --font-display: 'Fredericka the Great', cursive;
  --font-body: 'Space Mono', monospace;

  --border-wobbly: 255px 15px 225px 15px/15px 225px 15px 255px;
  --shadow-harsh: 4px 4px 0px var(--color-accent);
}
```
