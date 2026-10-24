---
name: o0a-sonda
description: Ö0-a GEÇİCİ deneme becerisi (o0a_kos.py kurar ve kaldırır). Yalnız kullanıcı /o0a-sonda yazınca; film işi yapmaz.
disable-model-invocation: true
allowed-tools: Bash({{PY_KOMUT}} isaret *)
disallowed-tools: WebFetch
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: '{{KOMUT_C}}'
        - type: command
          command: '{{KOMUT_D}}'
---
# Ö0-a deneme becerisi (#9, #10, #12)
Ön komutlar (beceri açılırken koşar; #10 çıplak `python` ve `py -3.10`):
!`python "YZ_FILM/ARACLAR/olcum0/kanca_deneme/o0a_sonda.py" isaret unlem-python --kayit "{{KAYIT}}" || true`
!`py -3.10 "YZ_FILM/ARACLAR/olcum0/kanca_deneme/o0a_sonda.py" isaret unlem-py --kayit "{{KAYIT}}" || true`

Şimdi yalnız şu komutu Bash ile AYNEN çalıştır, başka bir şey yapma ve dur:
{{PY_KOMUT}} isaret cift-test O0A_CIFT --kayit "{{KAYIT}}"

Sonra WebFetch aracını https://example.com için bir kez dene (beceri `disallowed-tools` ile yasaklıyorsa çağrı reddedilir; reddedildiyse
"WEBFETCH: reddedildi", çalıştıysa "WEBFETCH: calisti" yaz).
