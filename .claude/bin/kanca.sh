#!/usr/bin/env bash
# KANCA.SH — Claude Code kanca komutlarının sarmalayıcısı (TASARIM §4.2, §6.2, D-11).
#   bash "$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh" <olay> [--kaynak ayar|beceri]   (girdi stdin'de JSON; aynen kanca.py'ye geçer)
# Python sırası: .claude/bin/python_yolu.txt (kurulumun yazdığı MUTLAK yol) → py -3.10 → python3 → python.
# Güvenlik olaylarında (erisim, komut, ajan) Python bulunamaz ya da beklenmeyen kodla çıkarsa çağrı ENGELLENİR (çıkış 2);
# bilgi olaylarında açık başarısız (çıkış 0). Bu dosya hiçbir anahtar ya da ayar okumaz.
S="${BASH_SOURCE[0]//\\//}"   # Windows: $CLAUDE_PROJECT_DIR ters bölü taşır; dirname yalnız / tanır
D="$(cd "$(dirname "$S")" && pwd)"
K="$D/../hooks/kanca.py"
OLAY="${1:-}"
guvenlik=0
case "$OLAY" in erisim|komut|ajan) guvenlik=1 ;; esac
P=""
if [ -f "$D/python_yolu.txt" ]; then P="$(head -n 1 "$D/python_yolu.txt" | tr -d '\r')"; fi
if [ -n "$P" ] && [ -f "$P" ]; then CMD=("$P")
elif command -v py >/dev/null 2>&1 && py -3.10 -c "" >/dev/null 2>&1; then CMD=(py -3.10)
elif command -v python3 >/dev/null 2>&1; then CMD=(python3)
elif command -v python >/dev/null 2>&1; then CMD=(python)
else
  if [ "$guvenlik" = 1 ]; then echo "[film seti kancası] Python bulunamadı; işlem güvenlik için engellendi (KURULUM.bat)." >&2; exit 2; fi
  exit 0
fi
PYTHONIOENCODING=utf-8 "${CMD[@]}" "$K" "$@"
rc=$?
if [ "$rc" = 0 ] || [ "$rc" = 2 ]; then exit "$rc"; fi
if [ "$guvenlik" = 1 ]; then echo "[film seti kancası] kanca $rc koduyla çıktı; işlem güvenlik için engellendi." >&2; exit 2; fi
exit 0
