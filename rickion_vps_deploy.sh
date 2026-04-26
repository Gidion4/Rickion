#!/usr/bin/env bash
# ============================================================
#  RICKION — VPS deployment (Ubuntu 22.04 / 24.04)
# ============================================================
#  Aja FRESH Ubuntu-pilvipalvelimelle (DigitalOcean, Hetzner, Vultr
#  jne., ~5-10 €/kk). Rickion alkaa pyöriä 24/7 — työ tehdään vaikka
#  koneesi on pois päältä ja sinä nukut.
#
#  Setup:
#     1. Osta VPS (suositus: Hetzner CPX21, ~6 €/kk, riittävä)
#     2. Luo A-record: rickion.sinun-domain.tld → VPS IP
#     3. SSH VPS:lle roottina
#     4. Lataa ja aja:
#          curl -fsSL https://<your-host>/rickion_vps_deploy.sh \
#               | DOMAIN=rickion.sinun-domain.tld EMAIL=sinu@email.tld bash
#     5. Noin 4 minuuttia myöhemmin Rickion on pystyssä:
#          https://rickion.sinun-domain.tld
#
#  Tuote valmistuttuaan:
#     • Rickion Core systemd-palveluna, käynnistyy reboottien jälkeen
#     • Caddy TLS-proxylla (automaattinen Let's Encrypt -sertifikaatti)
#     • Obsidian Vault versioituu git-repoon päivittäin
#     • Agenttisilmukka pyörii jatkuvasti, tuottaa tulosta Vaultiin
#     • Mobiilista tai koneelta avaat UI:n HTTPS-osoitteesta
# ============================================================
set -euo pipefail

DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-admin@example.com}"
RICKION_USER="rickion"
INSTALL_DIR="/opt/rickion"
BRANCH="${BRANCH:-main}"

log(){ echo -e "\033[92m[rickion]\033[0m $*"; }
die(){ echo -e "\033[91m[error]\033[0m $*"; exit 1; }

[[ $EUID -eq 0 ]] || die "Aja rootina (sudo su)."
[[ -n "$DOMAIN" ]] || die "DOMAIN puuttuu. Esim: DOMAIN=rickion.example.com ./rickion_vps_deploy.sh"

log "1/7  Järjestelmäpäivitykset"
apt-get update -y >/dev/null
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y >/dev/null
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 python3-pip python3-venv git curl wget ufw \
    debian-keyring debian-archive-keyring apt-transport-https \
    ca-certificates gnupg build-essential >/dev/null

log "2/7  Palomuuri: vain 22 (SSH), 80, 443"
ufw --force reset >/dev/null
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow 22/tcp >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null

log "3/7  Rickion-käyttäjä + install-kansio"
id -u "$RICKION_USER" &>/dev/null || useradd -m -s /bin/bash "$RICKION_USER"
mkdir -p "$INSTALL_DIR"
chown -R "$RICKION_USER:$RICKION_USER" "$INSTALL_DIR"

log "4/7  Rickion-koodi + riippuvuudet"
cd "$INSTALL_DIR"
if [[ ! -f rickion_core.py ]]; then
    # Oleta että olet rsync-ännyt tiedostot tänne.
    # Vaihtoehtoisesti: clone private repo (lisää tähän git clone komento).
    log "HUOM: kopioi Rickion-tiedostot /opt/rickion/ ennen ajon jatkoa:"
    log "      scp -r ./RICKION/* root@$DOMAIN:/opt/rickion/"
    log "      Ja aja tämä skripti uudelleen."
    exit 0
fi
sudo -u "$RICKION_USER" python3 -m venv venv
sudo -u "$RICKION_USER" "$INSTALL_DIR/venv/bin/pip" install -U pip >/dev/null
sudo -u "$RICKION_USER" "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt >/dev/null

log "5/7  Systemd-palvelu — Rickion käynnistyy bootissa ja jatkuu ikuisesti"
cat > /etc/systemd/system/rickion.service <<EOF
[Unit]
Description=RICKION Core — autonomous multi-agent system
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RICKION_USER
Group=$RICKION_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/rickion_core.py
Restart=always
RestartSec=5
# Local-only WebSocket; public HTTPS goes through Caddy
Environment="PYTHONUNBUFFERED=1"
# Resource guards so a runaway agent doesn't eat the server
MemoryMax=2G
CPUQuota=180%

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable rickion >/dev/null
systemctl restart rickion
sleep 2
systemctl is-active --quiet rickion && log "   ✓ rickion.service active" || die "rickion.service failed — check: journalctl -u rickion -n 50"

log "6/7  Caddy TLS-proxy: serves UI + proxies WebSocket, auto Let's Encrypt"
if ! command -v caddy &>/dev/null; then
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null
    apt-get update -y >/dev/null
    apt-get install -y caddy >/dev/null
fi

cat > /etc/caddy/Caddyfile <<EOF
{
    email $EMAIL
}

$DOMAIN {
    encode zstd gzip

    # Serve the UI statically
    root * $INSTALL_DIR
    try_files {path} /rickion_command_center.html
    file_server

    # Proxy the WebSocket to the local Core
    @ws {
        header Connection *Upgrade*
        header Upgrade websocket
        path /ws*
    }
    handle @ws {
        reverse_proxy 127.0.0.1:8777
    }

    # Basic rate limits
    @abuse {
        header User-Agent "*bot*" "*scraper*" "*curl*"
    }
    respond @abuse "403" 403

    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options nosniff
        Referrer-Policy strict-origin-when-cross-origin
        Permissions-Policy "camera=(), geolocation=()"
        -Server
    }

    log {
        output file /var/log/caddy/rickion.log
        format console
    }
}
EOF
mkdir -p /var/log/caddy
systemctl enable caddy >/dev/null
systemctl restart caddy

log "7/7  Nightly Vault backup (git commit + optional GitHub push)"
cat > /etc/cron.daily/rickion-backup <<'EOF'
#!/bin/bash
cd /home/rickion/RickionVault 2>/dev/null || exit 0
sudo -u rickion git add -A
sudo -u rickion git commit -m "nightly snapshot $(date -I)" 2>/dev/null || true
if [[ -n "${GH_PUSH:-}" ]]; then
    sudo -u rickion git push origin main 2>/dev/null || true
fi
EOF
chmod +x /etc/cron.daily/rickion-backup

log ""
log "================================================================"
log "  ✓ RICKION ON VPS:LLÄ PYSTYSSÄ"
log ""
log "  UI:         https://$DOMAIN"
log "  Logit:      journalctl -u rickion -f"
log "  Restart:    systemctl restart rickion"
log "  Stop:       systemctl stop rickion"
log "  Vault:      /home/rickion/RickionVault"
log ""
log "  Rickion pyörii nyt 24/7. Sulje koneesi — se jatkaa."
log "================================================================"
