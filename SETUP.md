# Opsætning af Den Lille Hjælper

Hej Anders 📎 - her er den rolige opskrift til at få Den Lille Hjælper ind i Home Assistant.

Din config-mappe er:

```text
C:\Data\Docker\Home-assistant-core
```

Inde i containeren svarer den normalt til:

```text
/config
```

## 1. Placér filerne

Kopiér mapperne fra repoet til din Home Assistant config:

```text
packages/the_little_helper.yaml
custom_templates/the_little_helper.jinja
python_scripts/log_daily_completion.py
www/the_little_helper/
the_little_helper_history/
dashboards/the-little-helper.yaml
blueprints/automation/the_little_helper/pill_reminder_with_escalation.yaml
```

Tilføj dette i `configuration.yaml`, hvis det ikke allerede findes:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

## 2. Registrér dashboardet

```yaml
lovelace:
  mode: storage
  dashboards:
    the-little-helper:
      mode: yaml
      title: "📎 Den Lille Hjælper"
      icon: mdi:paperclip
      show_in_sidebar: true
      filename: dashboards/the-little-helper.yaml
```

## 3. Installer HACS-kort

Installer HACS, og tilføj:

1. `mushroom-cards`
2. `mini-graph-card`
3. `calendar-heatmap-card`
4. `button-card`
5. `bar-card`

## 4. Health Connect og Samsung Health

På Android: Samsung Health -> Health Connect -> Home Assistant Companion App -> Settings -> Companion app -> Manage sensors -> Health Connect: Steps.

Ret derefter `sensor.anders_phone_steps` i `packages/the_little_helper.yaml`.

## 5. Withings entities

Pakken forventer:

```text
sensor.withings_weight_anders
sensor.withings_systolic_blood_pressure_anders
sensor.withings_diastolic_blood_pressure_anders
sensor.withings_heart_pulse_anders
```

Ret YAML og dashboard, hvis dine entity IDs er anderledes.

## 6. Gym-zone

Ret koordinaterne for `zone.gym` i `packages/the_little_helper.yaml`.

## 7. Mobil og TTS

Ret disse placeholders:

```text
notify.mobile_app_anders_phone
media_player.living_room_speaker
person.anders
```

TTS bruger `tts.google_translate_say`. Skift til `tts.cloud_say`, hvis du bruger Nabu Casa.

## 8. Maskotbilleder

Læg disse filer i `C:\Data\Docker\Home-assistant-core\www\the_little_helper`:

```text
mascot_idle.png
mascot_thinking.png
mascot_celebrate.png
mascot_comfort.png
mascot_sleeping.png
```

## 9. Configuration diff

```diff
+homeassistant:
+  packages: !include_dir_named packages
+
+lovelace:
+  mode: storage
+  dashboards:
+    the-little-helper:
+      mode: yaml
+      title: "📎 Den Lille Hjælper"
+      icon: mdi:paperclip
+      show_in_sidebar: true
+      filename: dashboards/the-little-helper.yaml
+
+recorder:
+  purge_keep_days: 1825
+  include:
+    entities:
+      - input_boolean.morning_pills_taken
+      - input_boolean.evening_pills_taken
+      - sensor.daily_steps
+      - binary_sensor.steps_goal_met
+      - input_boolean.workout_completed_today
+      - sensor.withings_weight_anders
+      - sensor.withings_systolic_blood_pressure_anders
+      - sensor.withings_diastolic_blood_pressure_anders
+      - sensor.withings_heart_pulse_anders
+      - counter.pill_streak_days
+      - counter.steps_streak_days
+      - counter.workout_streak_weeks
+      - input_number.mood_morning
+      - input_number.mood_evening
+      - sensor.mood_delta_today
+  exclude:
+    domains:
+      - automation
+      - updater
```

Fem års SQLite-historik kan blive tungt. Brug MariaDB, hvis databasen bliver langsom:

```yaml
mariadb:
  image: mariadb:11
  environment:
    MYSQL_ROOT_PASSWORD: change-me
    MYSQL_DATABASE: homeassistant
    MYSQL_USER: homeassistant
    MYSQL_PASSWORD: change-me-too
  volumes:
    - ./mariadb:/var/lib/mysql
```

## Verifikation

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
- [ ] Mood prompt fires at 09:00 and 21:30.
- [ ] "Lav ugentlig rapport nu"-knappen genererer en rapport på dansk.
- [ ] Den automatiske ugentlige rapport fyrer søndag 20:00 og gemmes i `the_little_helper_history/reports/`.
- [ ] Dashboard "📎 Den Lille Hjælper" renderer uden fejl.
- [ ] Notifikationer åbner med persona-voice.
- [ ] TTS-prompt starter med "Hej Anders, Den Lille Hjælper her..."
- [ ] Maskot-billedet skifter ansigt baseret på `sensor.the_little_helper_mood`.
- [ ] Persona-toggle slår persona-formuleringer fra uden at deaktivere påmindelser.
- [ ] Tap maskot 3 gange -> easter egg notifikation fyrer.
- [ ] "Tips fra Hjælperen" viser et tip og roterer dagligt.
