American Poker Engine — Visual & System Spec v2.0
=================================================

Overview
--------

American Poker 2.0 (American Poker Engine) uses a retro 8-bit aesthetic with
pixel-perfect layout on a 32×18 grid (GU=8). This document captures the visual
specification, modular structure, round flow phases, auto-HOLD behavior, and
SFX package scaffold.

Project Structure (High-Level)
------------------------------

Start-up structure:

* ``main`` → ``switch`` (module toggles via true/false) → ``app`` (main hub).

Central modules:

* Render — minimalist visual layer (American Poker v2)
* Controller — lightweight facade that glues subsystems
* GameManager
* Economy
* Round Flow — single authoritative phase machine for a hand lifecycle

Scenes
------

Menu → Game Table → GAMBLE (red or black).

Grid System (32×18, GU=8)
-------------------------

Grid Layout System splits 256×144 px into 32×18 cells (8 px each). All UI and
scene elements align to grid cells (not absolute pixels), ensuring pixel-perfect
output with integer upscaling (×5 → 1280×720).

The grid provides:

* a single source of geometry for widgets and gameplay zones,
* layout presets (HAND_ZONE, HUD_ZONE, PAYTABLE_ZONE, etc.),
* fast layout and positioning (no manual coordinates),
* a dev overlay with grid lines and cell numbering (0–31, 0–17).

Result: a crisp retro pixel interface with predictable layout.

Auto HOLD
---------

How auto-HOLD works (simple view):

1. **Trigger**
   After 5 cards are dealt (DEAL). When deal animation finishes, auto-HOLD runs.
2. **Visual behavior**
   Holds are marked left-to-right with a small delay between cards so the player
   “sees the thought process.”
3. **Ownership**

   * **Policy** (``poker/hold/policy.py``): after deal, computes suggestion mask
     (5 booleans), stores in ``store.suggest`` but does not apply it.
   * **RoundFlow** (``round_flow.py``): reads suggestion and applies to
     ``store.mask`` in a staged sequence with delays; input is blocked during
     staging.
   * **Store** (``poker/hold/store.py``): holds current HOLD mask and suggestion;
     supports ``lock()``/``unlock()`` during animations.
   * **Renderer** (``render.py``): draws HELD badges from current mask; does not
     draw suggestion.

4. **Rules summary**

   * If already a pat hand (flush/straight/full house/4 of a kind, etc.) → hold all 5.
   * With Joker:
     * If a natural pair/trips exists → hold matches + all jokers.
     * Else 2–3 high cards suited (aiming straight-flush/royal) + jokers.
     * Else hold only joker(s).
   * Without Joker:
     * pair/two pair/trips/quads → 4 to a flush → 4 to open straight →
       3 to “almost royal” (suited) → 2 suited highs → single best high → nothing.

5. **After auto-HOLD**

   * Once staged highlighting finishes, Draw becomes active.
   * On Draw, replace all unheld cards; new deal begins afterward.

6. **Why**

   * Shows reasoning in steps.
   * Avoids sudden mask flip.
   * Locks prevent accidental override during staging.

Visual Design Specification v2.0
--------------------------------

1. Visual Philosophy
~~~~~~~~~~~~~~~~~~~~

Retro 90s casino terminal: neon accents, hard edges, stepped animation, and
pixel fonts. The display is digital, not photoreal.

Principles:

* Pixel-perfect (no anti-aliasing).
* Integer scaling only (×5).
* 8-bit clarity, hard lines.
* Electronic UI style.
* Functional neon accents for logic highlights.

2. Virtual Space
~~~~~~~~~~~~~~~~

* Virtual resolution: **256×144 px**
* Grid: **32×18** (8 px cell)
* Scale: **×5 → 1280×720**
* Layers: BG → Cards → FX → UI/HUD → Modals → Cursor
* Format: **16:9**

3. Palette (24-color minimum)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Background:** #000000, #001B8C, #0034FF
* **Panel background:** #00A0FF, #66E6FF, #0094D0
* **Borders:** #0038A8, #0A0A0A, #262626
* **Win accents:** #FF1F3C, #FF7A00, #FFD400
* **Main text:** #F2F2F2, #FFFFFF
* **Secondary text:** #9BD5FF, #5AA6FF
* **Suits:** ♥ #E61A3C, ♦ #FF3F5E, ♠ #101010, ♣ #1B1B1B
* **Green indicator:** #00C849, #2EE66B, border #0E612C
* **Neon turquoise:** #00F0FF

Palette must be indexed (8-bit PNG), ≤ 32 colors per screen.
No gradients; use stepped 2–3 shade bands without alpha.

5. Geometry and Grid
~~~~~~~~~~~~~~~~~~~~

* **GU (Grid Unit):** 8 px
* **Alignment:** all elements on 32×18 grid
* **Spacing:** 1–2 GU between blocks
* **Card size:** 7×10 GU (56×80 px)
* **Borders:** 1 virtual px, no rounding
* **Buttons/Panels:** strict rectangles

Layout zones (cells):

* **HAND_ZONE:** (3,6,26,8) — 5 cards
* **PAYTABLE_ZONE:** (24,1,7,12) — payout table
* **HUD_ZONE:** (1,14,10,3) — bet/credits
* **FX_ZONE:** (0,0,32,18) — effects
* **GAMBLE_MODAL_ZONE:** (7,4,18,10) — red/black modal

6. UI Elements
~~~~~~~~~~~~~~

Paytable
^^^^^^^^

* Background: #66E6FF
* Active row: yellow bar full width, no rounding
* Win text: #FF1F3C; other text: black
* Border: 1 px dark blue
* Row spacing: 1 GU
* Top label “250 COINS”: #00F0FF on blue

Cards
^^^^^

* Size: 56×80 px (virtual)
* Border: 1 px dark blue
* Back: 2-color pattern (white/blue)
* Face: 4-color pixel portrait, no half-tones
* Rank/suit: crisp with 1 px outline
* HELD badge: yellow text on blue (#001B8C), text #FFD400

HUD (bottom panel)
^^^^^^^^^^^^^^^^^^

* Background: black
* BET/CREDIT fields: blue background with bright yellow text
* “WALLET”: neon turquoise #00F0FF
* Panel borders: 1 px blue #0038A8
* Values right-aligned

Control buttons
^^^^^^^^^^^^^^^

* Rectangular buttons on black panel
* Colors:

  * **RED:** #E61A3C background, white text
  * **BLACK:** #101010 background, white text
  * **COLLECT / DRAW / DEAL:** white text 8 px

* Active state: brighter; inactive: 30% darker
* No gradients; pressed = inverted highlight (dark top row)

7. Effects & Highlights
~~~~~~~~~~~~~~~~~~~~~~~

* WIN banner: flashes between #FFD400 ↔ #FF7A00 every 150 ms
* HELD indicator: appears in steps (0.2 s between cards)
* Insert Coins: pulsing neon (brightness 100% → 60%)
* Draw/Deal press: 1-frame inverted brightness
* FX layer: minimal, discrete flashes/lines, no alpha glow
* Gamble modal: center slide-in, 2 px “bounce”, no easing

8. Pixel-Perfect Rules
~~~~~~~~~~~~~~~~~~~~~~

* All coordinates/sizes/offsets are integers.
* No float animations/positioning.
* Integer-only scaling (×5).
* Fonts rendered without anti-aliasing.
* No blur/transparency/soft shadows.
* Any motion uses 1 virtual px increments.

9. Visual Test Checklist
~~~~~~~~~~~~~~~~~~~~~~~~

* 400% zoom: square pixels, no gray halos.
* All elements are multiples of 8 px with clean spacing.
* Paytable active row spans full width.
* Buttons are rectangular with no gradients.
* Determination font is legible on any background.
* Colors strictly from palette (≤ 24 colors on screen).
* FPS stable at 60+, GridOverlay ≤ 0.3 ms.

10. Visual Formula
~~~~~~~~~~~~~~~~~~

**Visual Style = Pixel Precision × Neon Contrast × 90s Casino UI**

Typography System
-----------------

Two pixel fonts:

* **Determination Mono** — bold, neon display font for logos, big buttons,
  status labels (DRAW, WIN, INSERT COINS).
* **Minecraftia** — compact, readable system font for paytables, HUD, and
  numeric fields (BET 2, CREDIT 1998).

Both render pixel-perfect at 256×144 without anti-aliasing and aligned to GU.

RoundFlow Phases
----------------

1. **GAME_START**

   * 5 face-down cards.
   * UI available: tips/tutorial, Deal button active.
   * First Deal triggers intro-shuffle animation.

2. **INTRO_SHUFFLE**

   * Cards shift to the center slot; shuffle plays.
   * Input blocked (except Cancel/Back if present).
   * Transition: ``on_finished(intro_shuffle)`` → DEALING.

3. **DEALING**

   * Sequential deal animation: slots 1…5.
   * Deal blocked, HOLD unavailable.
   * After all 5 cards: → DEALT.

4. **DEALT**

   * Hand dealt, await input.
   * Manual HOLD enabled; auto-HOLD starts (L→R ticks).
   * Draw available; bet changes locked until hand ends.

5. **DRAWING**

   * Replace non-held cards, animation & SFX.
   * Deal/Draw locked.
   * After replacement → evaluate → SETTLED.

6. **SETTLED**

   * Highlight winning paytable line.
   * Payout to Economy (port).
   * Optional transition to GAMBLE or directly to ROUND_END.

7. **GAMBLE (optional)**

   * Controlled by Gamble adapter; RoundFlow awaits result.
   * Return win to Economy → ROUND_END.

8. **ROUND_END**

   * Clear HOLD, remove highlights, prep new deck/seed.
   * Auto transition to GAME_START (or IDLE if menu exists).

Minimal core loop:

``GAME_START → INTRO_SHUFFLE → DEALING → DEALT → DRAWING → SETTLED → ROUND_END``

SFX Package Scaffold
--------------------

1) Goals & Principles
~~~~~~~~~~~~~~~~~~~~~

* Immediate responsiveness: 40–200 ms sounds for actions & phases.
* Variation (2–4 variants) for frequent events (deal/draw/click/payout_tick).
* Unified architecture: SfxPort, volume buses, key→path registry.
* Hearing safety: debounce + music ducking during payouts.
* Small size + cross-platform: WAV for dev, OGG/Opus for prod.

2) Buses & Roles
~~~~~~~~~~~~~~~~

Buses (independent volume groups):

* ui — clicks/navigation/errors
* cards — deal/flip/hold/draw
* coins — payouts/credits/wins
* ambience — casino loop
* music — menu/table loops
* system — phase transitions (optional)

Recommended starting levels (multiplied by master):

* master: 0.8
* ui: 0.8
* cards: 0.9
* coins: 1.0
* ambience: 0.35
* music: 0.35
* system: 0.6

3) Asset Structure
~~~~~~~~~~~~~~~~~~

::

  assets/sfx/
    ui/
    cards/
    table/
    round/
    bet/
    credits/
    coins/
    amb/
    music/
    hold/

Naming:

* key = category/event, file = event_01.wav, event_02.wav, …
* loop tracks use ``_loop`` suffix.

4) Full Key List (MVP 1.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~

UI
^^

* ui/click (×3 variants, 40–80 ms)
* ui/hover (≤60 ms, debounce ≥120 ms)
* ui/toggle_on, ui/toggle_off (100–150 ms)
* ui/back (120–180 ms)
* ui/focus (60–100 ms)
* ui/notify (150–250 ms)
* ui/error (200–300 ms)
* ui/blocked (150–200 ms)

Cards / Table
^^^^^^^^^^^^^

* table/shuffle (600–900 ms)
* cards/deal (×4, 70–110 ms)
* hold/confirm (5 stepped sounds for auto-HOLD)
* cards/unhold (80–120 ms)
* cards/flip (×2, 50–80 ms)
* cards/draw (×3, 70–110 ms)
* table/clear (200–350 ms)

Round / System
^^^^^^^^^^^^^^

* round/ready (120–180 ms)
* round/settle (120–180 ms)

Economy / Coins / Credits
^^^^^^^^^^^^^^^^^^^^^^^^^

* bet/change_up, bet/change_down (100–140 ms)
* bet/max (150–200 ms)
* credits/in (200–250 ms)
* coins/win_small (300–400 ms)
* coins/win_medium (0.6–0.9 s)
* coins/payout_tick (×4, 40–60 ms)
* coins/payout_end (220–320 ms)

Ambience / Music
^^^^^^^^^^^^^^^^

* amb/casino (20–40 s loop)
* music/menu, music/table (one loop each)

5) Registry Format (Example)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  {
    "ui/click": ["ui/click_01.wav", "ui/click_02.wav", "ui/click_03.wav"],
    "ui/hover": ["ui/hover_01.wav"],
    "ui/blocked": ["ui/blocked_01.wav"],
    "ui/notify": ["ui/notify_01.wav"],
    "ui/toggle_on": ["ui/toggle_on_01.wav"],
    "ui/toggle_off": ["ui/toggle_off_01.wav"],
    "ui/back": ["ui/back_01.wav"],
    "ui/focus": ["ui/focus_01.wav"],
    "ui/error": ["ui/error_01.wav"],

    "table/shuffle": ["table/shuffle_01.wav"],
    "table/clear": ["table/clear_01.wav"],
    "cards/deal": ["cards/deal_01.wav", "cards/deal_02.wav", "cards/deal_03.wav", "cards/deal_04.wav"],
    "cards/flip": ["cards/flip_01.wav", "cards/flip_02.wav"],
    "cards/unhold": ["cards/unhold_01.wav"],
    "cards/draw": ["cards/draw_01.wav", "cards/draw_02.wav", "cards/draw_03.wav"],

    "round/ready": ["round/ready_01.wav"],
    "round/settle": ["round/settle_01.wav"],

    "bet/change_up": ["bet/change_up_01.wav"],
    "bet/change_down": ["bet/change_down_01.wav"],
    "bet/max": ["bet/max_01.wav"],
    "credits/in": ["credits/in_01.wav"],
    "coins/win_small": ["coins/win_small_01.wav"],
    "coins/win_medium": ["coins/win_medium_01.wav"],
    "coins/payout_tick": ["coins/payout_tick_01.wav", "coins/payout_tick_02.wav", "coins/payout_tick_03.wav", "coins/payout_tick_04.wav"],
    "coins/payout_end": ["coins/payout_end_01.wav"],

    "amb/casino": ["amb/casino_loop.wav"],
    "music/menu": ["music/menu_loop.wav"],
    "music/table": ["music/table_loop.wav"],

    "hold/confirm": ["hold/hold_01.wav", "hold/hold_02.wav", "hold/hold_03.wav", "hold/hold_04.wav", "hold/hold_05.wav"]
  }

6) RoundFlow Mapping (Call Sites)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``on_intro_shuffle_start()`` → ``table/shuffle``
* ``on_deal_card(i)`` → ``cards/deal``
* ``on_all_dealt()`` → ``round/ready``
* ``on_auto_hold_step(i)`` → ``hold/confirm`` (variant by index)
* ``on_unhold(card)`` → ``cards/unhold``
* ``on_confirm_hold(card)`` → ``cards/flip``
* ``on_draw_card(i)`` → ``cards/draw``
* ``on_settle_start()`` → ``round/settle``
* ``on_payout_tick()`` → ``coins/payout_tick``
* ``on_payout_end()`` → ``coins/payout_end``
* ``on_table_clear()`` → ``table/clear``

7) Playback Rules
~~~~~~~~~~~~~~~~~

* Variant randomization + slight pitch jitter (±3–5%) for deal/draw/payout/click.
* Throttling:

  * ui/hover — no more than 1 per 120–150 ms per widget.
  * cards/deal/draw — 70–110 ms between cards.

* Music ducking:

  * coins/win_* and coins/payout_* → reduce music to 0.25–0.40, recover in 300–600 ms.
  * table/shuffle → reduce music to ~0.30 during shuffle.

* Blocked input during animations should play ``ui/blocked``.
* Default volumes are listed in section 2; individual clips may be scaled.

8) File Requirements
~~~~~~~~~~~~~~~~~~~~

* Dev: WAV, 44.1 kHz, mono, 16-bit PCM.
* Prod: OGG/Opus for long loops; WAV for ultra-short SFX if needed.
* Normalize peaks to −1…0 dBFS; equalize loudness by ear.
* Loops (*_loop): seamless, no clicks, 30–100 ms fades.

9) Compatibility & Extensibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Keep keys stable; swap files without changing keys.
* Add new events under their respective categories.
* Extend with ``coins/win_big`` or ``jackpot`` as needed.

10) SFX Test Checklist (DoD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* All keys load without missing paths.
* Each RoundFlow phase triggers expected events without double-triggering.
* Hover is throttled; deal/draw maintain intervals.
* Music ducks/recovers on payouts.
* No clipping/clicks; no CPU spikes with payout ticks.
* NullSfx backend preserves flow without blocking.
