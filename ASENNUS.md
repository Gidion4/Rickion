# RICKION — Asennus työpöydälle

> Päämäärä: Rickion omana sovelluksena koneesi työpöydällä. Tuplaklikkaat kuvaketta → Rickion aukeaa omassa ikkunassaan → toimii heti paikallisesti.

---

## Ennen kuin aloitat (2 min)

Tarvitset **Python 3.10 tai uudemman**. Tarkista avaamalla terminaali / komentorivi:

```bash
python --version
```

Jos saat ilmoituksen "command not found" tai versio on < 3.10:

- **Windows**: [python.org/downloads](https://www.python.org/downloads/) → asenna 3.12. **Muista laittaa ruksi "Add Python to PATH"** asennuksessa.
- **macOS**: `brew install python@3.12` tai python.orgista
- **Linux**: `sudo apt install python3.12 python3-pip` (Ubuntu/Debian)

---

## NOPEA ASENNUS — 3 vaihetta

### 1. Pura tämä kansio koneellesi pysyvään paikkaan

Esimerkiksi:
- **Windows**: `C:\Rickion\`
- **macOS / Linux**: `~/Rickion/` (eli `/Users/sinun-nimi/Rickion/`)

**Älä pura sitä latauskansioon** jota siivoat — tänne Rickion jää asumaan.

### 2. Avaa terminaali tuossa kansiossa ja aja asentaja

**Windows (komentokehote tai PowerShell):**
```powershell
cd C:\Rickion
python install_desktop.py
```

**macOS / Linux (Terminal):**
```bash
cd ~/Rickion
python3 install_desktop.py
```

Asentaja tekee automaattisesti:
1. Asentaa Python-riippuvuudet (`websockets`, `google-generativeai`, `pywebview`, jne.)
2. Generoi Rickion-ikonin (portal-vihreä "R")
3. Luo **"Rickion"-kuvakkeen työpöydällesi**
4. (Valinnainen) Rekisteröi autostartin — Rickion manifestoituu kun avaat koneen

### 3. Tuplaklikkaa "Rickion" työpöydällä

Rickion aukeaa omassa natiivi-ikkunassa. Ei selainriviä, ei välilehtiä — ihan oma sovellus.

**Ensimmäisellä käynnistyksellä:**
1. Mene **Configuration**-välilehdelle
2. Liitä Gemini API-avaimesi ([hanki tästä](https://aistudio.google.com/apikey))
3. Paina SAVE, sitten TEST GEMINI
4. Mene **Persona**-välilehdelle
5. Paina SPACE ja puhu — Rickion kuuntelee ja vastaa ääneen

Valmis. Rickion on koneellasi.

---

## TÄYSI JARVIS-MODE (manifestoituu koneen käynnistyessä)

Jos haluat että Rickion käynnistyy automaattisesti kun avaat koneen (kuten Jarvis):

```bash
python install_desktop.py --autostart
```

Tämä rekisteröi Rickionin:
- **Windows**: Task Scheduler (`ONLOGON`)
- **macOS**: `~/Library/LaunchAgents/com.rickion.core.plist`
- **Linux**: `~/.config/autostart/rickion.desktop`

Kun seuraavan kerran kirjaudut sisään, Rickion Core käynnistyy taustalle automaattisesti. Voit avata UI:n työpöytäkuvakkeesta milloin tahansa — Core on jo lämmin.

### Pysäyttäminen

```bash
python rickion_core.py --stop
```

Palauttaminen:

```bash
python rickion_core.py --unstop
```

---

## MITÄ TYÖPÖYDÄLLÄSI ON ASENNUKSEN JÄLKEEN

**Windows:**
- `Työpöytä\Rickion.lnk` — tuplaklikkaa avataksesi

**macOS:**
- `~/Desktop/Rickion.app` — klikkaa tai tuplaklikkaa

**Linux:**
- `~/Desktop/Rickion.desktop` — klikkaa (saattaa kysyä "Trust" ensimmäisellä kerralla)

---

## TIEDOSTORAKENNE — mikä asuu missä

```
C:\Rickion\  (tai ~/Rickion/)
│
├── rickion_command_center.html   ← UI (natiivi-ikkuna avaa tämän)
├── rickion_core.py               ← paikallinen ydin (WebSocket, Gemini, Obsidian)
├── rickion_app.py                ← natiivi-ikkuna-käynnistin (pywebview)
├── install_desktop.py            ← asentaja (aja kerran)
├── requirements.txt              ← riippuvuudet
├── rickion_launch.bat / .sh      ← vaihtoehtoinen käynnistin (selain-moodi)
├── assets\rickion.ico / .icns / .png
├── ASENNUS.md                    ← tämä tiedosto
└── RICKION_SETUP.md              ← arkkitehtuuri + tietoturva
```

**Rickion tuottaa käytössä (koti-kansioosi):**

```
~/.rickion/                       ← paikallinen state, lokit, STOP-tiedosto
├── state.json                    ← agentit, proposals, cycle
├── keys.json  (fallback)
├── rickion.log
└── proposals\

~/Documents/RickionVault/         ← OBSIDIAN VAULT (primäärimuisti)
├── Rickion Core Identity.md
├── Phoenix Protocol.md
├── Cognitive Architecture.md
├── Goals.md
├── Agents\
├── Pipelines\
├── Claude Produced\
├── Episodic\
└── Logs\
```

---

## JOS JOKIN EI TOIMI

### "python: command not found"
Asenna Python uudelleen ja valitse **"Add Python to PATH"**. Tai kokeile `python3` `python`:n sijasta.

### "pywebview ei löytynyt" tai natiivi-ikkuna ei aukea
Rickion avautuu silloin oletussläimessä — kaikki toimii silti. Voit yrittää:
```bash
pip install pywebview --upgrade
```
Windowsissa saattaa vaatia `WebView2` runtime:n (yleensä esiasennettu Win10/11:ssa).

### Natiivi-ikkuna mustana
Tämä on Windowsin Edge WebView2 -ongelma. Lataa ja asenna:
[WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)

### "Access denied" Obsidian Vaultiin
Tarkista että `~/Documents/` on kirjoitettavissa. Tai vaihda vault-polku Configurationissa toiseen kansioon.

### Ikoni ei näy työpöydällä
Osa käyttöjärjestelmistä tarvitsee refreshin. Klikkaa työpöytää hiiren oikealla → Refresh. Tai luo shortcut manuaalisesti: target = `python rickion_app.py`, working dir = Rickion-kansion polku.

### Gemini ei vastaa
Tarkista avain Configurationissa. Testaa **TEST GEMINI** -napilla. Jos vika jää, testaa avain suoraan [Google AI Studiossa](https://aistudio.google.com/).

---

## VALINNAINEN: TEE RICKIONISTA OIKEA EXE/APP (PyInstaller)

Jos haluat bakata koko Rickionin yhdeksi `Rickion.exe` -tiedostoksi jota voi kantaa tikulla (ei vaadi Pythonin asennusta muilla koneilla):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed \
  --icon=assets/rickion.ico \
  --add-data "rickion_command_center.html:." \
  --add-data "rickion_core.py:." \
  --name Rickion \
  rickion_app.py
```

Tuloksena `dist/Rickion.exe` (Windows) / `dist/Rickion.app` (macOS). Tämä on standalone — ei vaadi Pythonia muualla.

---

## TIETOTURVA-MUISTUTUS

- Rickion Core bindaa vain **127.0.0.1**. Ei avaa porttia internetiin.
- API-avaimet menevät OS keyringiin ensisijaisesti, tiedostoon vain jos keyring puuttuu (tällöin tiedosto saa 600-oikeudet).
- Obsidian Vault on lokaali. GitHub-backup on **valinnainen** ja **privaatti** (asentaja ei pushaa sinne, vasta kun kytket PAT + repo Vaultin asetuksissa).
- Kaikki kaupankäynti-moduulit käynnistetään sinun manuaalisella käskylläsi.

---

**Seuraavat askeleet** (kun Rickion on pystyssä):

1. Avaa Persona-välilehti, testaa puhetta
2. Engageoi AUTONOMY (yläpalkin oikea reuna) — Rickion alkaa ajatella itsenäisesti
3. Spawna ensimmäinen agenttilegioona (Agent Factory → SPAWN LEGION)
4. Sano komentosilllalla: *"Rickion, generoi ensimmäinen konkreettinen rahantekoputki Freedom Indexin nostamiseen."*

Ja pois lähtee.
