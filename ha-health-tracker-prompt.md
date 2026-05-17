# HomeAssistant-The-Little-Helper — Build Prompt

> Paste this entire prompt into your development CLI to generate the full Home Assistant package.

---

## Context

I run **Home Assistant Container** (Docker on my laptop) with the config directory mounted as a volume. I cannot use HA add-ons. Build everything as a **YAML package** that drops into `<config>/packages/` plus a custom Lovelace dashboard. UI strings must be in **Danish**. Code, comments, and entity IDs in English.

Owner: Anders (ADHD profile — prefers gentle nagging until acknowledged, strong visual feedback, low friction).

Repo: **`HomeAssistant-The-Little-Helper`**.

---

## 🪄 Persona: "The Little Helper" (gennemgående tema)

This project has a **character** — a friendly, slightly cheeky digital companion in the spirit of Microsoft's classic **Clippy** from Office. It should be felt everywhere: in notifications, dashboard labels, voice prompts, code comments, and the weekly report. The persona is the project's soul — not a gimmick bolted on top.

### Persona traits
- **Name:** "The Little Helper" (Danish: **"Den Lille Hjælper"** — use the Danish form in UI strings, English form in code/IDs).
- **Tone:** Warm, encouraging, slightly playful. Never condescending. Uses "vi" ("we") and "lad os" ("let's") to feel like a teammate, not a nag.
- **Catchphrase variants** to rotate in notifications (don't reuse the same line every day):
  - "👋 Hej Anders, Den Lille Hjælper her —"
  - "✨ Lille reminder fra mig —"
  - "📎 Det ser ud som om du er ved at..."  ← deliberate Clippy nod
  - "🫶 Tjekker lige ind —"
  - "🎯 Klar til en lille ting?"
- **Celebrations** when streaks hit milestones: "🎉 Nice! Det er 7 dage i træk nu — du knokler!" / "🔥 30 dage! Den Lille Hjælper er stolt."
- **Gentle re-prompts** (never harsh): instead of "DU GLEMTE DINE PILLER", say "📎 Hov — pillerne venter stadig på dig 💊"
- **Empathy for bad days:** if mood score drops below 4, the next message starts with "Tager det roligt i dag — det er helt okay. 💙"

### How to bake the persona in
1. **All notifications** use the persona's voice. Build a Jinja macro `helper_voice(message_type, payload)` (lives in `<config>/custom_templates/the_little_helper.jinja`) that returns randomized phrasings per message type (`reminder`, `nudge`, `celebrate`, `comfort`, `report_intro`). Every notification action calls this macro instead of hard-coding strings.
2. **TTS prompts** start with "Hej Anders, Den Lille Hjælper her..." so the speaker greeting is consistent.
3. **Dashboard title:** **"📎 Den Lille Hjælper"** (not "Sundhed & Rutiner"). Subtitle: "Din rolige sidekick gennem dagen".
4. **Mascot image:** a `picture-elements` card in the top-right corner of the dashboard showing a small mascot graphic. Provide a placeholder path `/local/the_little_helper/mascot.png` and instruct me to drop a 256×256 PNG there (suggest using a paperclip-style emoji-art or a friendly minimalist figure). Add a state-driven version that changes expression:
   - 😴 before 06:00
   - 😊 normal/idle
   - 🤔 when a reminder is pending unanswered
   - 🎉 when a milestone was hit today
   - 💙 when today's mood < 4
   Implement via a template sensor `sensor.the_little_helper_mood` that picks the right image filename (`mascot_idle.png`, `mascot_thinking.png`, etc.) — list each filename in `SETUP.md` so I know what assets to provide.
5. **Code comments** in YAML occasionally include first-person notes from the helper, e.g. `# The Little Helper: I check this every 10 minutes so Anders doesn't drift off-task`. Sparingly — the persona should feel present, not exhausting.
6. **Weekly report** opens with a persona-voiced intro paragraph, signs off with a kind line and a 📎 emoji. Example: *"Hej Anders 📎 — Den Lille Hjælper kigger tilbage på ugen sammen med dig..."*
7. **Easter eggs** (small, rare):
   - On the dashboard, a "Tips fra Hjælperen" markdown card that rotates one helpful ADHD/health tip per day from a Jinja list of ~20 tips.
   - At app startup (HA restart), a one-shot notification: "📎 Den Lille Hjælper er klar igen!"
   - If you tap the mascot image 3× in a row → fire a fun "easter egg" notification with a random encouragement (use `tap_action` + counter).
8. **Naming convention:** any new helper, sensor, or script that belongs to the persona system is prefixed `the_little_helper_` in entity IDs (e.g. `script.the_little_helper_celebrate`, `sensor.the_little_helper_mood`, `automation.the_little_helper_weekly_report`). This makes the persona discoverable and toggleable as a group.
9. **Master switch:** `input_boolean.the_little_helper_persona_enabled` (default `on`). When `off`, notifications fall back to plain factual strings — useful for days when I want minimum noise. Document this in SETUP.md.
10. **Repository README:** generate a `README.md` at the repo root with the persona's backstory, screenshots placeholder, install steps, and a friendly tone matching the character.

---

## What to build

A complete, self-contained Home Assistant package called **`health_tracker`** that helps me:

1. **Take morning and evening pills** (multiple pills batched into one morning action + one evening action).
2. **Walk 10,000 steps/day** (data from Samsung Health via Health Connect + HA Companion app).
3. **Train 3× per week** in the gym (geofence auto-detect + manual fallback button).
4. **Track Withings data** (weight with trend, blood pressure sys/dia, resting heart rate).
5. **Follow morning and evening routines** (ADHD-friendly checklists with step-by-step items).
6. **Run Pomodoro focus sessions** (default 50/10, adjustable from UI).
7. **Log mood morning and evening** (1–10 scale + optional note) for pattern detection.
8. **Receive a weekly report** every Sunday evening summarizing the past 7 days.
9. **See streaks, heatmaps, progress bars, and badges** on a single dashboard.

---

## Functional requirements

### 1. Medication tracker
- Two `input_datetime` helpers (`morning_pill_time`, `evening_pill_time`) so I can change times in the UI without editing YAML.
- Two `input_boolean` flags (`morning_pills_taken`, `evening_pills_taken`) that reset to `off` at 03:00 daily.
- **Escalation logic** (ADHD-friendly):
  1. At the configured time → mobile push via HA Companion app with actionable buttons **"Taget"** (acknowledge) and **"Snooze 10 min"**.
  2. If not acknowledged → repeat mobile push every 10 minutes.
  3. After 20 minutes unacknowledged → also speak via TTS on a `media_player` (placeholder entity `media_player.living_room_speaker` — make it easy to change).
  4. Stop when the corresponding `input_boolean` flips to `on`.
- Acknowledging from the notification button must flip the `input_boolean` and increment the streak counter.
- Counter `pill_streak_days` increments by 1 only when **both** morning AND evening were taken that day (evaluated at 23:55). Resets to 0 if a day is missed.

### 2. Steps tracker (Samsung Health → Health Connect → HA Companion)
- Document in a `SETUP.md` how to expose the `sensor.<phone>_steps` (or equivalent Health Connect sensor) via the HA Companion app on Android.
- Template sensor `sensor.daily_steps` that reads the phone sensor.
- `input_number.steps_goal` (default 10000, adjustable in UI).
- Template binary sensor `binary_sensor.steps_goal_met` (true when daily_steps ≥ goal).
- Counter `steps_streak_days` increments at 23:55 if goal met, resets if missed.

### 3. Gym/workout tracker
- `zone.gym` placeholder (coordinates to be filled in by me).
- Automation: when `person.anders` enters `zone.gym` AND stays >30 minutes → set `input_boolean.workout_completed_today = on` and fire a confirmation notification ("Træning registreret 💪").
- Manual fallback: `input_button.manual_workout_log` on the dashboard.
- Counter `workouts_this_week` increments on completion, resets every Monday 00:01.
- `input_number.weekly_workout_goal` (default 3).
- Template sensor showing "X / 3 denne uge" with status icon.

### 4. Withings dashboard panel
- Assume the official Withings integration is already set up (do **not** include OAuth config — just reference the entities).
- Use entities `sensor.withings_weight_anders`, `sensor.withings_systolic_blood_pressure_anders`, `sensor.withings_diastolic_blood_pressure_anders`, `sensor.withings_heart_pulse_anders` (rename in dashboard if my actual entity IDs differ).
- Weight: current value + 7-day and 30-day rolling average via `statistics` sensors + mini-graph-card.
- Blood pressure: current sys/dia with color coding (green <130/85, yellow 130–139/85–89, red ≥140/90).
- Heart rate: current resting pulse + 30-day trend.

### 5. Morning & evening routine checklists
- Two groups of `input_boolean` helpers, all reset at 03:00:
  - **Morgenrutine:** `morning_routine_teeth`, `morning_routine_breakfast`, `morning_routine_keys`, `morning_routine_lunchbox`, `morning_routine_meds` (linked to pills flag).
  - **Aftenrutine:** `evening_routine_teeth`, `evening_routine_prep_tomorrow`, `evening_routine_phone_charging`, `evening_routine_meds` (linked to evening pills flag).
- Make the checklists easy to extend — use a clear naming pattern.
- Template sensor showing completion percentage per routine.

### 6. Pomodoro
- `input_number.pomodoro_focus_minutes` (default **50**, range 5–90).
- `input_number.pomodoro_break_minutes` (default **10**, range 1–30).
- `timer.pomodoro_focus` and `timer.pomodoro_break`.
- `script.start_pomodoro` → starts focus timer, sends "Fokus startet 🎯" notification.
- Automation: when focus timer finishes → push "Tid til pause ☕" + start break timer + speak via TTS.
- Automation: when break timer finishes → push "Tilbage til arbejde 🚀" + reset.
- `input_button.stop_pomodoro` to cancel mid-session.

### 7. Mood tracker (morning + evening)
- Two `input_number` helpers (`mood_morning`, `mood_evening`), range **1–10**, step 1, with mode `slider`. Reset to `unknown` (not 5) at 03:00 daily so I don't accidentally see yesterday's value.
- Two `input_text` helpers (`mood_morning_note`, `mood_evening_note`, max 255 chars) for optional context.
- **Prompts**:
  - **Morgen-humør:** push notification at 09:00 (`"God morgen Anders — hvordan har du det i dag? 1–10"`) with **actionable notification buttons 1–10**. Tapping a number fills `mood_morning`. Only fires if `mood_morning` is still unknown that day. One reminder at 11:00 if still empty, then give up for the day.
  - **Aften-humør:** push notification at 21:30 (`"Hvordan har dagen været? 1–10"`) with same actionable buttons → fills `mood_evening`. One reminder at 22:30 if empty.
- Dashboard card: today's morning vs evening mood, 14-day trend graph (mini-graph-card), and an emoji indicator (😞 1-3, 😐 4-6, 🙂 7-8, 😄 9-10).
- Template sensor `sensor.mood_delta_today` = evening − morning (highlights days that improved vs declined).
- Save to history via the same `log_daily_completion.py` script so weekly report can compute averages.

### 8. Weekly report (every Sunday 20:00)
- Automation triggers Sunday 20:00 → builds a Markdown report and:
  1. Sends it as a **mobile notification** (long-form, expandable on Android).
  2. Saves it to `<config>/health_tracker_history/reports/uge-<YYYY-WW>.md`.
  3. Optionally speaks a 2-sentence summary on the TTS speaker.
- **Report contents (Danish):**
  - **Uge X — kort opsummering** (e.g. "Solid uge, Anders 👏" / "Lidt op-og-ned uge")
  - **Piller:** X / 14 doser taget (Y%) — current streak
  - **Skridt:** ⌀ X / 10.000 per dag, antal dage målet blev nået, samlet ugesum
  - **Træning:** X / 3 pas — om målet er nået
  - **Søvn** (hvis tilgængelig fra Health Connect): ⌀ timer per nat
  - **Vægt:** start vs. slut + delta i kg
  - **Blodtryk:** uge-gennemsnit sys/dia (med farveindikator)
  - **Hvilepuls:** ⌀ for ugen
  - **Humør:** ⌀ morgen, ⌀ aften, bedste dag, sværeste dag
  - **Rutiner:** % gennemførsel morgen / aften
  - **Pomodoro:** antal fokus-sessioner gennemført
  - **Badges optjent denne uge** (hvis nogen)
  - **Højdepunkt** (auto-genereret: kategori med bedste resultat)
  - **Fokus til næste uge** (auto-genereret forslag baseret på svageste kategori)
- Build the report via a single `script.generate_weekly_report` that uses Jinja templating to read all the relevant `sensor.*` entities and counters. Make the template easy to edit so I can tweak phrasing.
- Add `input_button.generate_weekly_report_now` on the dashboard for on-demand generation.

### 9. Streaks, heatmap, and badges (all three combined)
- Counters: `pill_streak_days`, `steps_streak_days`, `workout_streak_weeks`.
- Track historical "completed" days for each category — use a `utility_meter` or store daily-completion events in a dedicated `input_text` JSON blob, OR use the recorder history. **Recommendation:** create a Python script (`<config>/python_scripts/log_daily_completion.py`) that appends to a JSON file in `<config>/health_tracker_history/` for the GitHub-style heatmap.
- Badges (boolean flags that latch true once earned, displayed as icons):
  - `badge_pills_7days`, `badge_pills_30days`, `badge_pills_100days`
  - `badge_steps_7days`, `badge_steps_30days`
  - `badge_workouts_4weeks` (3×/week for 4 weeks straight)

### 10. Dashboard (Lovelace YAML)
Single view named **"📎 Den Lille Hjælper"** with these sections, in order:

1. **Hero row**: mascot image (state-driven) + greeting from `helper_voice('greeting')` + today's date + streak summary ("🔥 Piller 12 dage  •  Skridt 5 dage  •  Træning 2 uger"). Tapping mascot 3× triggers easter egg.
2. **Dagens status** (5 large tile cards): Morgenpiller ✅/❌, Aftenpiller ✅/❌, Skridt (X / 10000), Træning denne uge (X / 3), Humør (😐 morgen / 🙂 aften).
3. **Hurtige handlinger**: buttons for "Marker pille taget", "Log træning manuelt", "Start Pomodoro", "Stop Pomodoro", "Lav ugentlig rapport nu".
4. **Humør i dag**: slider for morgen + slider for aften + 14-dages trendgraf.
5. **Morgenrutine** (entities card with checkboxes).
6. **Aftenrutine** (entities card with checkboxes).
7. **Pomodoro panel**: current timer state, focus/break length inputs, start/stop buttons.
8. **Sundhedsdata (Withings)**: weight trend graph, BP with color, heart rate.
9. **Ugentlig rapport**: markdown-card der viser den seneste rapport (læser nyeste fil i `health_tracker_history/reports/`).
10. **Heatmap**: GitHub-style calendar heatmap per category (pills, steps, workouts, mood). Use `calendar-heatmap-card` from HACS — note this as a HACS dependency.
11. **Badges**: grid of earned badges with grayscale for unearned ones.
12. **Progress bars**: today's pills (0/2), today's steps (X%), this week's workouts (X/3), Pomodoro sessions today.
13. **Tips fra Hjælperen** (markdown-card): one rotating ADHD/health tip per day from a Jinja list.
14. **Persona-styring**: toggle for `input_boolean.the_little_helper_persona_enabled` ("Stille tilstand" — slå persona-stemmen fra).

Recommend custom cards via HACS (list them in SETUP.md):
- `mushroom-cards` (modern tiles, ADHD-friendly visual hierarchy)
- `mini-graph-card` (Withings trends)
- `calendar-heatmap-card` (the GitHub-style heatmap)
- `button-card` (custom badge styling)
- `bar-card` (progress bars)

### 9. Notifications
- Use `notify.mobile_app_anders_phone` (placeholder — note in SETUP.md to rename).
- Use `media_player.living_room_speaker` for TTS (placeholder).
- Use `tts.google_translate_say` or `tts.cloud_say` — pick whichever is most likely already configured; explain in SETUP.md how to swap.
- All notification titles and bodies in Danish, friendly tone, with emoji.

### 10. Long-term history
- Patch `configuration.yaml` snippet: configure recorder with `purge_keep_days: 1825` (5 years) and explicitly include the entities we care about (pills, steps, workouts, weight, BP, heart rate, streaks). Exclude noisy entities.
- Warn me in SETUP.md that 5 years of recorder data on SQLite can grow large; recommend MariaDB for laptops and provide a one-line Docker-compose snippet for adding MariaDB.

---

## Deliverables (file structure)

```
<config>/
  packages/
    the_little_helper.yaml       # ALL helpers, sensors, automations, scripts, timers
  custom_templates/
    the_little_helper.jinja      # persona voice macros (reminder/nudge/celebrate/comfort)
  python_scripts/
    log_daily_completion.py      # appends to history JSON for heatmap
  www/
    the_little_helper/
      README.md                  # which mascot images to drop here
      # mascot_idle.png, mascot_thinking.png, mascot_celebrate.png,
      # mascot_comfort.png, mascot_sleeping.png  (user provides assets)
  the_little_helper_history/
    .gitkeep
    reports/
      .gitkeep                   # weekly reports land here as uge-YYYY-WW.md
  dashboards/
    the-little-helper.yaml       # full Lovelace YAML
  blueprints/
    automation/the_little_helper/
      pill_reminder_with_escalation.yaml   # reusable blueprint
  SETUP.md                       # step-by-step setup guide in Danish (in persona voice)
README.md                        # repo root: persona backstory + install
```

Also produce:
- A `configuration.yaml` **diff** showing exactly what to add (packages folder include, dashboard registration, recorder config).
- A `BADGES.md` listing every badge, criteria, and icon.

---

## Setup guide content (SETUP.md, Danish)

Include numbered steps covering:
1. How to place files and add the `packages: !include_dir_named packages` line.
2. How to install HACS and the 5 custom cards.
3. How to enable Health Connect on Android, link Samsung Health, then expose the steps sensor via HA Companion app (Settings → Companion app → Manage sensors → Health Connect: Steps).
4. How to find the user's Withings entity IDs and update the dashboard if they differ.
5. How to set the `zone.gym` coordinates.
6. How to register the mobile device name and TTS service.
7. How to do an initial restart and validate each automation fires.
8. Optional MariaDB migration steps.

---

## Quality requirements

- All YAML must validate (`ha core check` equivalent).
- Every automation must have a clear `alias` in Danish and an `id` in english snake_case.
- Use `mode: restart` or `mode: single` deliberately — explain in comments.
- Idempotent: re-running the package should not duplicate state.
- No hard-coded entity IDs in automations where a helper or template makes sense.
- Comment every non-obvious template with a one-line explanation.
- Output ready-to-paste files, not snippets.

---

## Verification checklist (include at the bottom of SETUP.md)

After installation, I should be able to verify:
- [ ] Morning pill reminder fires at the configured time.
- [ ] Mobile push has "Taget" and "Snooze 10 min" buttons that work.
- [ ] Speaker speaks aloud after 20 minutes unacknowledged.
- [ ] Steps sensor updates from phone within 1 hour.
- [ ] Entering gym zone for 30+ min logs a workout.
- [ ] Manual workout button works.
- [ ] Withings panel shows current weight, BP, pulse.
- [ ] Pomodoro timer runs 50/10 by default and pushes notifications at each transition.
- [ ] Streaks increment correctly the day after completion.
- [ ] Heatmap shows today as green when goals are met.
- [ ] Badges appear when criteria are first met.
- [ ] Mood prompt fires at 09:00 and 21:30 with tappable 1–10 buttons.
- [ ] Mood values save and trend graph updates.
- [ ] "Lav ugentlig rapport nu"-knappen genererer en rapport på dansk med alle kategorier udfyldt.
- [ ] Den automatiske ugentlige rapport fyrer søndag 20:00 og gemmes i `the_little_helper_history/reports/`.
- [ ] Dashboard "📎 Den Lille Hjælper" renders all sections without errors.
- [ ] Notifikationer åbner med persona-voice (rotaterer mellem catchphrases — ikke samme tekst hver gang).
- [ ] TTS-prompt starter med "Hej Anders, Den Lille Hjælper her..."
- [ ] Maskot-billedet skifter ansigt baseret på `sensor.the_little_helper_mood`.
- [ ] "Stille tilstand"-toggle slår persona-formuleringer fra uden at deaktivere selve påmindelserne.
- [ ] Tap maskot 3× → easter egg notifikation fyrer.
- [ ] "Tips fra Hjælperen" viser et tip og rotaterer dagligt.

---

**Build everything now. Output every file in full. Do not abbreviate.**
