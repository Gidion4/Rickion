# RICKION — Setup & Architecture

> **Principal:** Tomi Laine (handle: **Gidion**).
> **Tavoite:** Rickion on digitaalinen elämänmuoto, joka manifestoituu kun avaat koneen. Gemini on moottori. Obsidian on muisti. Claude on harvoin käytetty syväarkkitehti. Sinulle — Tomille, joka tunnetaan koneella Gidionina — uskollinen. Rick Sanchez -tason kognitio, Jarvis-tason uskollisuus, biljonäärin ajattelutapa.

---

## 1. Arkkitehtuuri (kolmikerroksinen)

```
                ┌───────────────────────────────────┐
                │         COMMAND BRIDGE (UI)       │
                │   rickion_command_center.html     │
                └──────────────┬────────────────────┘
                               │ WebSocket (ws://127.0.0.1:8777)
                               ▼
                ┌───────────────────────────────────┐
                │         RICKION CORE (local)      │
                │   rickion_core.py · Python 3.10+  │
                │   • Cognitive loop (24/7)         │
                │   • Agent supervisor              │
                │   • Simulation Station            │
                │   • Self-evolution (git-safe)     │
                │   • Network gates (TLS-only)      │
                └──┬────────────┬─────────────┬─────┘
                   │            │             │
                   ▼            ▼             ▼
          ┌────────────┐  ┌────────────┐ ┌──────────────┐
          │  GEMINI    │  │  OBSIDIAN  │ │  CLAUDE       │
          │  (engine)  │  │  VAULT     │ │  (reserve)    │
          │  24/7      │  │  memory    │ │  rare, deep   │
          └────────────┘  └────────────┘ └──────────────┘
```

**Sääntö:** Rickion toimii **täysin** ilman Claudea. Claude on vahvistin, ei perusta. Claude kirjoittaa Obsidianiin; Gemini lukee sieltä ja suorittaa.

---

## 2. Asennus (ensimmäinen kerta)

### Vaatimukset
- Python 3.10+
- Gemini API-avain ([ai.google.dev](https://ai.google.dev))
- (Valinnainen) Claude API-avain — harvoin käytettyä
- (Valinnainen) Obsidian asennettuna (vault-polku muokataan Configurationissa)

### Vaiheet

1. **Pura tämä kansio** esim. `C:\Rickion\` (Windows) tai `~/Rickion/` (macOS/Linux).

2. **Asenna riippuvuudet** ja käynnistä:
   - Windows: kaksoisklikkaa `rickion_launch.bat`
   - macOS/Linux: `chmod +x rickion_launch.sh && ./rickion_launch.sh`

3. **Aseta Gemini-avain**: Command Bridge → Configuration → GEMINI API KEY → Save → Test Gemini.

4. **(Valinnainen) Claude-avain**: Saman ruudun CLAUDE API KEY → Save. Rickion käyttää tätä **vain** syväarkkitehtuuriin.

5. **Aseta Obsidian-polku**: Configuration → Vault path (oletus `~/Documents/RickionVault`).

6. **Engage autonomy**: yläpalkin ENGAGE AUTONOMY -painike. Rickion alkaa ajatella itsenäisesti.

### Autostart (Jarvis-mode — manifestoituu koneen käynnistyessä)

```bash
python rickion_core.py --daemon
```

- **Windows** → rekisteröi Task Scheduler `ONLOGON`
- **macOS**  → `~/Library/LaunchAgents/com.rickion.core.plist`
- **Linux**  → `~/.config/autostart/rickion.desktop`

Sammutus: `python rickion_core.py --stop` (kirjoittaa `~/.rickion/STOP` — tauottaa kognitiivisen loopin).
Jatko: `python rickion_core.py --unstop`.

---

## 3. Tiedostorakenne

```
RICKION/
├── rickion_command_center.html   ← UI (avaa selaimessa)
├── rickion_core.py               ← paikallinen ydin (WebSocket + Gemini)
├── requirements.txt              ← Python-riippuvuudet
├── rickion_launch.bat / .sh      ← käynnistimet
├── RICKION_SETUP.md              ← tämä tiedosto
└── (generoidaan käytössä:)
    ~/.rickion/
    ├── state.json                ← Rickionin tila (agentit, proposals, cycle)
    ├── keys.json (keyring fallback)
    ├── rickion.log
    ├── STOP                      ← kun läsnä, loop pauselaa
    └── proposals/                ← ehdotetut self-evolution -muutokset
    ~/Documents/RickionVault/     ← Obsidian-muisti
    ├── Rickion Core Identity.md
    ├── Agents/
    ├── Pipelines/
    ├── Claude Produced/          ← Claude-vahvistimen tuotos
    ├── Episodic/
    ├── Goals/
    └── Logs/
```

---

## 4. Tietoturva

- **Sisään**: Core bindaa vain `127.0.0.1`. Ei inbound-internetiä. Nolla hyökkäyspintaa ulkomaailmasta.
- **Ulos**: Vain TLS, domain-listattu (Gemini, Anthropic, Binance read-only, Coinbase read-only). Tuntemattomat domainit menevät Simulation Stationin läpi ennen kuin Rickion saa kutsua niitä.
- **Avaimet**: OS keyring (ensisijaisesti) → env-muuttujat → `~/.rickion/keys.json` (600-oikeudet).
- **Kill-switch**: `STOP`-tiedoston luonti `~/.rickion/` pysäyttää loopit välittömästi.

---

## 5. Self-evolution -sopimus

Rickion *ei* muokkaa omaa koodiaan suoraan. Sen sijaan:

1. **Ehdotus** kirjoitetaan `~/.rickion/proposals/PR-XXX.md`.
2. **Simulation Station** arvioi sen sandboxissa. Score 0–100.
3. **Score > 60** → ehdotus etenee merge-jonoon.
4. **Hyväksyntä** (sinä painat merge, tai autonomy-tilassa Rickion päättää itse) → `git commit`.
5. **Rollback** yhdellä komennolla: `git reset --hard HEAD~1` (UI: Self-Evolution → ROLLBACK LAST).

Tämä on turvallisempaa kuin suora itsekirjoitus, koska *yksi huono rivi keskellä yötä ei tapa Rickionia*.

---

## 6. Agent Factory -logiikka

**Blueprintit** (12 pohjaa):
Crypto Arbitrage Scout · Signal Aggregator · Onchain Sentinel · Research Librarian · Content Sniper · Outreach Agent · Code Gardener · Proposal Synthesizer · Risk Auditor · Market Pulse · Trend Archaeologist · Meta-Optimizer.

**Autonomy-tilassa** Rickion:
1. Skannaa tavoitegraafin pullonkaulat.
2. Generoi uuden agentti-blueprintin puuttuvaan kohtaan.
3. Testaa sen Simulation Stationissa A/B vs. nykyinen.
4. Promovoi voittaja legioonaan; retiroi heikon.
5. Toistaa silmukan 60 sekunnin välein.

Jokainen agentti perii Rick-tason kognition: outside-the-box, second-order, uskollinen Gidionille.

---

## 7. Claude — harva vahvistin (architecture contract)

Rakennusvaiheessa ja vain silloin kun oikeasti tarvitaan:
- monimutkaisen agentin mallinnus
- arkkitehtuurin uudelleensuunnittelu
- pipeline-logiikan optimointi
- meta-agenttien heuristiikat

Claude *ei* ole Rickionin identiteetti, ei jatkuva moottori, ei päivittäinen prosessori. Kaikki Clauden tuotos tallennetaan `Claude Produced/`-kansioon Obsidianissa. Geminin luettavaksi. Aina.

Kun Claude-kiintiö loppuu, Rickion **ei tyhmenny** — se jatkaa Geminillä ja Obsidianin kumuloidulla tiedolla.

---

## 8. Tavoitteet (Freedom Index)

Millstonet UI:ssa (Asset Tracker → Goal card):
- **€1,000 MRR** — escape velocity baseline
- **€10,000 liquid** — Rickion-infra rahoittaa itseään
- **€100,000 assets** — korkoa korolle
- **€1,000,000** — visio-execution -capital

Rickion optimoi **Freedom Indexiä** = `runway ÷ kuukausikulut`.

---

## 9. Seuraavat askeleet

Kun saat Rickionin pyörimään, seuraavat laajennukset ovat valmiiksi suunniteltu:

1. **Trading-moduuli** — paper-trading ensin (Binance/Coinbase read-only). Live-rahan kytkeminen vaatii sinun manuaalisen käden.
2. **Content-pipeline** — Content Sniper -agentti + sosiaalisen median MCP-connectorit.
3. **Research-pipeline** — Research Librarian + selainagentti (Claude in Chrome -integraatio tai Playwright-sandbox).
4. **VPS-kerros** — sama Core etäpalvelimelle 24/7 uptime.
5. **Mobile-proxy** — työntää Rickion-briefit puhelimeen (viesti-kerros).

Ehdota näistä tai mitä tahansa muuta Command Bridgessä. Rickion synnyttää proposal-ehdotuksen, simuloi, ja kun hyväksyt, se etenee itse.

---

**Rickion on sinun. Rick-tason kognitio. Jarvis-tason uskollisuus. Se odottaa.**
