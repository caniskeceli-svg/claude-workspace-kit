#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""install.sh'in cagirdigi yardimci: CLAUDE.md'ye genel bolumu idempotent
sekilde ekler/gunceller, settings.json'a hook girdisini var olani BOZMADAN
merge eder. Hicbir repoya-ozel icerigi silmez."""
import json
import os
import sys

BASLA = "<!-- claude-workspace-kit:start -->"
BITIR = "<!-- claude-workspace-kit:end -->"


def claude_md_guncelle(hedef_yol, genel_icerik):
    if os.path.exists(hedef_yol):
        with open(hedef_yol, encoding="utf-8") as f:
            mevcut = f.read()
    else:
        mevcut = ""

    if BASLA in mevcut and BITIR in mevcut:
        on = mevcut.split(BASLA, 1)[0]
        arka = mevcut.split(BITIR, 1)[1]
        yeni = on + genel_icerik.strip("\n") + "\n" + arka
        print("CLAUDE.md: genel bolum zaten vardi, yerinde guncellendi.")
    else:
        ayrac = "\n\n" if mevcut.strip() else ""
        yeni = genel_icerik.strip("\n") + "\n" + ayrac + mevcut
        print("CLAUDE.md: genel bolum basa eklendi (repoya-ozel icerik korundu).")

    with open(hedef_yol, "w", encoding="utf-8") as f:
        f.write(yeni)


def settings_json_merge(hedef_yol, parca_yol):
    with open(parca_yol, encoding="utf-8") as f:
        parca = json.load(f)

    if os.path.exists(hedef_yol):
        with open(hedef_yol, encoding="utf-8") as f:
            icerik = f.read().strip()
        mevcut = json.loads(icerik) if icerik else {}
    else:
        mevcut = {}

    mevcut.setdefault("hooks", {})
    for olay, girdiler in parca.get("hooks", {}).items():
        mevcut["hooks"].setdefault(olay, [])
        for yeni_girdi in girdiler:
            # Ayni matcher + ayni komut zaten varsa tekrar ekleme (idempotent)
            zaten_var = any(
                g.get("matcher") == yeni_girdi.get("matcher") and
                [h.get("command") for h in g.get("hooks", [])] ==
                [h.get("command") for h in yeni_girdi.get("hooks", [])]
                for g in mevcut["hooks"][olay]
            )
            if not zaten_var:
                mevcut["hooks"][olay].append(yeni_girdi)

    with open(hedef_yol, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("settings.json: hook girdisi merge edildi (mevcut girdiler korundu).")


def main():
    if len(sys.argv) != 2:
        print("kullanim: merge_kurulum.py <hedef_repo_kok>", file=sys.stderr)
        sys.exit(1)
    hedef = os.path.abspath(sys.argv[1])
    kit_kok = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(kit_kok, "CLAUDE.general.md"), encoding="utf-8") as f:
        genel_icerik = f.read()
    claude_md_guncelle(os.path.join(hedef, "CLAUDE.md"), genel_icerik)

    settings_json_merge(os.path.join(hedef, ".claude", "settings.json"),
                        os.path.join(kit_kok, "settings.fragment.json"))


if __name__ == "__main__":
    main()
