# Main Screen UI Concept (Command Center)

## 1) Design principle

Main screen is a unified political HQ dashboard, not separate disconnected windows.

Layout logic:
- center: **who controls power now**;
- left: **country and geography**;
- right: **player party state**;
- top: **timeline + system pressure**;
- bottom: **events + available actions this turn**.

## 2) Global layout zones

1. **Top strategic bar**
   - `Turn X/100`
   - current stage label
   - full cycle progress strip
   - country pressure indicators
   - quick mode navigation tabs

2. **Center (upper)**
   - Saeima semicircle (100 seats)
   - coalition arithmetic (`56/100`, etc.)
   - coalition stress visual cues

3. **Left panel**
   - Latvia map (5 districts for MVP)
   - map mode toggles: influence/support/network/turnout/protest/topic/coalition geography

4. **Left lower panel**
   - electoral segment cards (7 segments)
   - per segment: current support, segment size, growth potential, trend

5. **Right panel (party state)**
   - party header + leader + current institutional status
   - rating/mandates/trend/coalition value block
   - 10 core resource indicators
   - warnings/opportunities block

6. **Right lower (government/targets)**
   - if in government: owned portfolios + operating effects
   - if opposition: current cabinet vulnerabilities and attack windows

7. **Center lower (public agenda pulse)**
   - 6–8 topics with temperature
   - controller of topic
   - usefulness to player

8. **Bottom strip**
   - event headlines feed
   - 3–5 context-sensitive actions for current turn

## 3) Stage-aware emphasis without layout reset

UI architecture stays stable; emphasis shifts by stage:
- Mandate phases: parliament/coalition/portfolios are primary.
- Pre-election assembly: party panel + segments + network gain emphasis.
- Hot campaign: map + segments + campaign tempo gain emphasis.

## 4) Visual style

- analytic political dashboard (not cartoon)
- clean typography
- restrained color coding
- trend arrows/heat strips over decorative effects
- low visual noise, high information density
