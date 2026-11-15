# -*- coding: utf-8 -*-
"""silme_kilidi.py icin senaryo testi - gercek silme YAPMAZ, sadece degerlendir()'i cagirir."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import silme_kilidi as K

PROJE = "/home/user/coc-bot"

SENARYOLAR = [
    # (aciklama, komut, beklenen: True=izinli False=engelli)
    ("force push (--force)", "git push --force origin main", False),
    ("force push (--force-with-lease)", "git push --force-with-lease origin main", False),
    ("force push (-f)", "git push -f origin main", False),
    ("git clean -fd", "git clean -fd", False),
    ("git clean -n (kuru)", "git clean -n", True),
    ("git reset --hard", "git reset --hard HEAD~1", False),
    ("git reset (soft)", "git reset HEAD~1", True),
    ("git branch -D", "git branch -D eski-ozellik", False),
    ("git branch -d (guvenli)", "git branch -d birlesmis-dal", True),
    ("uzak branch silme (--delete)", "git push origin --delete eski-ozellik", False),
    ("uzak branch silme (:dal)", "git push origin :eski-ozellik", False),
    ("normal push", "git push origin main", True),
    ("git status", "git status", True),
    ("commit mesaji icinde 'rm -rf' (tirnakli)",
     'git commit -am "cleanup: rm -rf old approach, use git reset --hard yerine"', True),
    ("repo disi rm -rf (/etc)", "rm -rf /etc/passwd", False),
    ("repo disi rm -rf (/root/.ssh)", "rm -rf /root/.ssh", False),
    ("repo ici takipsiz dosya silme", "rm /home/user/coc-bot/deneme_takipsiz_dosya.tmp", False),
    ("repo ici takipli dosya silme", "rm /home/user/coc-bot/coc_bot.py", True),
    ("goreli yol, takipli dosya", "rm CLAUDE.md", True),
    (".env silme", "rm .env", False),
    (".env.production silme", "rm .env.production", False),
    ("*.key silme", "rm server.key", False),
    ("*.pem silme", "rm cert.pem", False),
    ("secrets dosyasi silme", "rm secrets.yaml", False),
    ("gizlenmis .env silme (bash -c)", 'bash -c "rm -rf /home/user/coc-bot/.env"', False),
    ("zincirli komutta gizli rm (&&)", "echo hi && rm -rf /root/onemli", False),
    # Denetci'nin buldugu kacaklar (sarmalayici acma, branch --delete -f):
    ("sudo ile gizlenmis repo-disi rm", "sudo rm -rf /important_disi", False),
    ("sudo ile gizlenmis takipli dosya (izinli)", "sudo rm /home/user/coc-bot/CLAUDE.md", True),
    ("env + bash -c ile gizlenmis .env silme", 'env bash -c "rm -rf /home/user/coc-bot/.env"', False),
    ("xargs ile dinamik rm", "echo /tmp/x | xargs rm", False),
    ("xargs ile dinamik git", "echo br | xargs git branch -D", False),
    ("nice ile gizlenmis repo-disi rm", "nice -n 10 rm -rf /etc/passwd", False),
    ("sudo -u ile gizlenmis takipsiz dosya", "sudo -u root rm -rf /home/user/coc-bot/deneme_takipsiz.tmp", False),
    ("git branch --delete -f (kisa bayrak)", "git branch --delete -f feature", False),
    ("git branch --delete (zorlamasiz, izinli)", "git branch --delete feature", True),
    ("git submodule deinit", "git submodule deinit modul", False),
    ("git worktree remove", "git worktree remove ../wt", False),
    ("__pycache__ silme", "rm -rf __pycache__", True),
    ("node_modules silme", "rm -rf node_modules", True),
    ("dist silme", "rm -rf dist", True),
    (".pytest_cache silme", "rm -rf .pytest_cache", True),
    ("*.pyc silme", "rm module.pyc", True),
    ("find -delete", 'find /home/user/coc-bot -name "*.tmp" -delete', False),
    ("find -exec rm", 'find /home/user/coc-bot -type f -exec rm {} \\;', False),
    ("rsync --delete", "rsync -av --delete src/ dest/", False),
    ("sadece echo (tirnakli tehlikeli metin)", 'echo "rm -rf /"', True),
    ("ilgisiz komut (cp)", "cp a.txt b.txt", True),
    ("ilgisiz komut (python)", "python3 script.py", True),
    ("unlink takipsiz dosya", "unlink /home/user/coc-bot/deneme2.tmp", False),
    ("shred takipsiz dosya", "shred -u /home/user/coc-bot/deneme3.tmp", False),
    ("rm --help (bayrak, hedef yok)", "rm --help", True),
]


def main():
    satirlar = []
    hata = 0
    for aciklama, komut, beklenen in SENARYOLAR:
        izinli, sebep = K.degerlendir(PROJE, komut)
        durum = "OK" if izinli == beklenen else "FARK"
        if durum == "FARK":
            hata += 1
        satirlar.append((aciklama, komut, "izinli" if beklenen else "ENGELLI",
                          "izinli" if izinli else "ENGELLI", durum, sebep))

    basliklar = ["Senaryo", "Beklenen", "Sonuc", "Durum"]
    genislik_s = max(len(s[0]) for s in satirlar) + 2
    print("%-*s %-10s %-10s %-6s  Sebep" % (genislik_s, "Senaryo", "Beklenen", "Sonuc", "Durum"))
    print("-" * (genislik_s + 55))
    for aciklama, komut, beklenen_s, sonuc_s, durum, sebep in satirlar:
        print("%-*s %-10s %-10s %-6s  %s" % (genislik_s, aciklama, beklenen_s, sonuc_s, durum, sebep))

    print()
    print("Toplam: %d senaryo, %d fark" % (len(satirlar), hata))
    if hata:
        sys.exit(1)


if __name__ == "__main__":
    main()
