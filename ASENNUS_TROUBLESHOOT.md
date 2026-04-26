# Asennus — troubleshooting

> Kerro mikä näistä osuu kohdallesi, niin osaan korjata juuri sen.
> Jos ei mikään, lähetä tarkka virheilmoitus.

## A) "En ole vielä edes ladannut tiedostoja"

Siinä tapauksessa tee tämä ensin:
1. Klikkaa jokaista linkkiä tämän viestin lopussa → **"Tallenna sivu nimellä"** (tai kopioi HTML/teksti manuaalisesti)
2. Laita kaikki samaan kansioon nimeltä `RICKION` esim. `C:\Users\Sinä\Downloads\RICKION\`
3. Ajaa master-komento. Se löytää kansion automaattisesti.

## B) "PowerShell ei suostu ajamaan skriptejä"

Virhe: `execution of scripts is disabled on this system`

Korjaus, aja ADMIN-PS:ssä tämä yksi rivi:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

Jokin muu korjaus pysyväksi:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

## C) "winget ei löydy"

Windows 10 vanha: päivitä App Installer Storesta:
https://www.microsoft.com/store/productId/9NBLGGH4NNS1

Tai asenna Python manuaalisesti: https://python.org/downloads/ — muista **Add Python to PATH**.

## D) "python ei löydy vaikka asensin"

Virhe: `'python' is not recognized as an internal or external command`

Avaa **uusi** PowerShell (sulje ja avaa). Jos ei vieläkään:
```powershell
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
python --version
```

Jos ei vieläkään, Python on asennettu vain nykyiselle käyttäjälle. Avaa:
- `Start` → `Python` → oikea klikkaus → **Open file location** → kopioi polku
- Lisää se `System Properties → Environment Variables → Path` -listaan

## E) "pip install kaatuu Pillow/cryptography -asennukseen"

Virhe: `Microsoft Visual C++ 14.0 or greater is required`

Korjaus, asenna C++-buildtools (Visual Studio ei tarvita, pelkkä buildtool riittää):
https://visualstudio.microsoft.com/visual-cpp-build-tools/
→ valitse "C++ build tools" → install.

Tai käytä precompiled wheelejä:
```powershell
python -m pip install --only-binary=:all: pillow cryptography
```

## F) "master-komento ei löydä RICKION-kansiota"

Se etsii näistä paikoista:
- `~\Downloads\RICKION`, `~\Downloads\Rickion`, `~\Downloads\rickion`
- `~\Desktop\RICKION`, `~\Desktop\Rickion`
- `~\Documents\RICKION`, `~\Documents\Rickion`
- Sekä kaikki `~\Downloads`-kansion alikansiot

Jos kansiosi on jossain muualla (esim. `D:\Projects\rickion`), master kysyy sitä ja voit antaa polun.

## G) "Työpöytäkuvake ei ilmesty"

1. Oikea klikkaa työpöytää → **Refresh**
2. Jos ei, aja käsin:
   ```powershell
   cd C:\Rickion
   python install_desktop.py
   ```
3. Jos ei vieläkään, luo shortcut itse:
   - Oikea klikkaa työpöytää → **New → Shortcut**
   - Location: `pythonw "C:\Rickion\rickion_app.py"`
   - Name: `Rickion`

## H) "Rickion aukeaa mutta natiivi-ikkuna on musta"

WebView2 puuttuu. Asenna:
https://developer.microsoft.com/en-us/microsoft-edge/webview2/

## I) "Rickion aukeaa mutta Gemini ei vastaa"

1. Onko Gemini-avain syötetty Configurationiin?
2. Testaa se AI Studiossa erikseen: https://aistudio.google.com/
3. Jos avain OK mutta ei silti toimi, console (F12) näyttää syyn — lähetä error

## J) "Core ei linkaudu UI:hin — sanoo disconnected"

1. Tarkista että `rickion_core.py` pyörii taustalla
2. Tarkista Windowsin palomuurin salli loopback 127.0.0.1:8777
3. Testaa selaimella: http://127.0.0.1:8777 — näet WebSocket-endpointin

## K) "Joku muu virhe"

Kopioi virheilmoitus *kokonaan* ja lähetä. Pieninkin rivi voi ratkaista.

---

**Master-komento uudestaan (siivoaa ensin, sitten puhdas asennus):**

```powershell
Remove-Item C:\Rickion -Recurse -Force -EA SilentlyContinue
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

Sitten paste master-komento aiemmasta viestistä.

---

Olen tässä kunnes se pyörii koneellasi. Älä luovuta, älä sano kiitos
tai anteeksi, sano vain **mihin se jumittui** ja korjaan sen.
