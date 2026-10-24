#!/usr/bin/env bash
# SONDA.SH — Ö0-a #8: kanca komutunun Git Bash ile `bash "$CLAUDE_PROJECT_DIR/…"` biçiminde çalıştığını ve sarmalayıcı süresini ölçer.
# Python sırası kanca.sh ile aynı: .claude/bin/python_yolu.txt → py -3.10 → python3 → python. Sonda bilgi kancasıdır: her durumda çıkış 0
# (işaretli deneme kodları hariç; onları o0a_sonda.py verir). Hiçbir anahtar ya da ayar okumaz.
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K="$D/o0a_sonda.py"
PY_YOLU="$D/../../../../.claude/bin/python_yolu.txt"
export O0A_SARMAL_BAS_NS="$(date +%s%N 2>/dev/null)"
case "$O0A_SARMAL_BAS_NS" in *N*|"") O0A_SARMAL_BAS_NS="" ;; esac
P=""
if [ -f "$PY_YOLU" ]; then P="$(head -n 1 "$PY_YOLU" | tr -d '\r')"; fi
if [ -n "$P" ] && [ -f "$P" ]; then CMD=("$P")
elif command -v py >/dev/null 2>&1 && py -3.10 -c "" >/dev/null 2>&1; then CMD=(py -3.10)
elif command -v python3 >/dev/null 2>&1; then CMD=(python3)
elif command -v python >/dev/null 2>&1; then CMD=(python)
else exit 0
fi
PYTHONIOENCODING=utf-8 "${CMD[@]}" "$K" "$@"
rc=$?
if [ "$rc" = 3 ]; then exit 3; fi
exit 0
