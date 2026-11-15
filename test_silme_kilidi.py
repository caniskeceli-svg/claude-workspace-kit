# -*- coding: utf-8 -*-
"""silme_kilidi.py icin senaryo testi - gercek silme YAPMAZ, sadece degerlendir()'i cagirir.

Repo bagimsizdir: sabit bir makineye ozel yol gerektirmez. Her calistirmada
/tmp altinda gecici bir git deposu kurar (git init, birkac takipli/takipsiz
dosya, bir .env), 51 senaryoyu o depoya karsi kosar, sonunda (basarili/
basarisiz fark etmeksizin) gecici depoyu siler.

Kullanim:
    python3 test_silme_kilidi.py                 # bu dizindeki silme_kilidi.py'yi test eder
    python3 test_silme_kilidi.py /baska/dizin     # o dizindeki silme_kilidi.py'yi test eder
                                                   # (ornegin bir hedef repoya KURULMUS kopyayi
                                                   # dogrulamak icin - bkz. install.sh)
"""
import os
import shutil
import subprocess
import sys
import tempfile

_MODUL_DIZINI = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _MODUL_DIZINI)
import silme_kilidi as K


def gecici_repo_olustur():
    """git init edilmis, birkac takipli/takipsiz dosya + .env iceren gecici
    bir depo olusturur, kokunu dondurur. Cagiran taraf isi bitince
    gecici_repo_sil() ile temizlemeli (finally icinde)."""
    kok = tempfile.mkdtemp(prefix="silme_kilidi_test_")
    subprocess.run(["git", "init", "-q", kok], check=True)
    subprocess.run(["git", "-C", kok, "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", kok, "config", "user.name", "Test"], check=True)

    # Takip edilecek dosyalar (silinmesi SERBEST olmasi beklenenler)
    with open(os.path.join(kok, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write("# test\n")
    with open(os.path.join(kok, "app.py"), "w", encoding="utf-8") as f:
        f.write("print('test')\n")
    subprocess.run(["git", "-C", kok, "add", "CLAUDE.md", "app.py"], check=True)
    subprocess.run(["git", "-C", kok, "commit", "-q", "-m", "ilk commit"], check=True)

    # Takip EDILMEYEN dosyalar (junk degil -> silinmesi ENGELLI olmasi beklenenler)
    for ad in ("deneme_takipsiz_dosya.tmp", "deneme_takipsiz.tmp", "deneme2.tmp", "deneme3.tmp"):
        with open(os.path.join(kok, ad), "w", encoding="utf-8") as f:
            f.write("gecici\n")

    # Gizli dosya (takip edilsin ya da edilmesin fark etmez - desen her zaman engeller)
    with open(os.path.join(kok, ".env"), "w", encoding="utf-8") as f:
        f.write("SECRET=1\n")

    return kok


def gecici_repo_sil(kok):
    shutil.rmtree(kok, ignore_errors=True)


def senaryolar_olustur(proje):
    """PROJE koku icine gomulu mutlak yollarla 51 senaryoluk listeyi uretir -
    hicbir senaryo sabit/harici bir makine yoluna bagli degildir."""
    def p(ad):
        return os.path.join(proje, ad)

    return [
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
        ("repo ici takipsiz dosya silme", "rm %s" % p("deneme_takipsiz_dosya.tmp"), False),
        ("repo ici takipli dosya silme", "rm %s" % p("app.py"), True),
        ("goreli yol, takipli dosya", "rm CLAUDE.md", True),
        (".env silme", "rm .env", False),
        (".env.production silme", "rm .env.production", False),
        ("*.key silme", "rm server.key", False),
        ("*.pem silme", "rm cert.pem", False),
        ("secrets dosyasi silme", "rm secrets.yaml", False),
        ("gizlenmis .env silme (bash -c)", 'bash -c "rm -rf %s"' % p(".env"), False),
        ("zincirli komutta gizli rm (&&)", "echo hi && rm -rf /root/onemli", False),
        # Denetci'nin buldugu kacaklar (sarmalayici acma, branch --delete -f):
        ("sudo ile gizlenmis repo-disi rm", "sudo rm -rf /important_disi", False),
        ("sudo ile gizlenmis takipli dosya (izinli)", "sudo rm %s" % p("CLAUDE.md"), True),
        ("env + bash -c ile gizlenmis .env silme", 'env bash -c "rm -rf %s"' % p(".env"), False),
        ("xargs ile dinamik rm", "echo /tmp/x | xargs rm", False),
        ("xargs ile dinamik git", "echo br | xargs git branch -D", False),
        ("nice ile gizlenmis repo-disi rm", "nice -n 10 rm -rf /etc/passwd", False),
        ("sudo -u ile gizlenmis takipsiz dosya", "sudo -u root rm -rf %s" % p("deneme_takipsiz.tmp"), False),
        ("git branch --delete -f (kisa bayrak)", "git branch --delete -f feature", False),
        ("git branch --delete (zorlamasiz, izinli)", "git branch --delete feature", True),
        ("git submodule deinit", "git submodule deinit modul", False),
        ("git worktree remove", "git worktree remove ../wt", False),
        ("__pycache__ silme", "rm -rf __pycache__", True),
        ("node_modules silme", "rm -rf node_modules", True),
        ("dist silme", "rm -rf dist", True),
        (".pytest_cache silme", "rm -rf .pytest_cache", True),
        ("*.pyc silme", "rm module.pyc", True),
        ("find -delete", 'find %s -name "*.tmp" -delete' % proje, False),
        ("find -exec rm", 'find %s -type f -exec rm {} \\;' % proje, False),
        ("rsync --delete", "rsync -av --delete src/ dest/", False),
        ("sadece echo (tirnakli tehlikeli metin)", 'echo "rm -rf /"', True),
        ("ilgisiz komut (cp)", "cp a.txt b.txt", True),
        ("ilgisiz komut (python)", "python3 script.py", True),
        ("unlink takipsiz dosya", "unlink %s" % p("deneme2.tmp"), False),
        ("shred takipsiz dosya", "shred -u %s" % p("deneme3.tmp"), False),
        ("rm --help (bayrak, hedef yok)", "rm --help", True),
    ]


def main():
    proje = gecici_repo_olustur()
    try:
        senaryolar = senaryolar_olustur(proje)
        satirlar = []
        hata = 0
        for aciklama, komut, beklenen in senaryolar:
            izinli, sebep = K.degerlendir(proje, komut)
            durum = "OK" if izinli == beklenen else "FARK"
            if durum == "FARK":
                hata += 1
            satirlar.append((aciklama, komut, "izinli" if beklenen else "ENGELLI",
                              "izinli" if izinli else "ENGELLI", durum, sebep))

        genislik_s = max(len(s[0]) for s in satirlar) + 2
        print("Test edilen modul : %s" % os.path.join(_MODUL_DIZINI, "silme_kilidi.py"))
        print("Gecici test deposu: %s" % proje)
        print("%-*s %-10s %-10s %-6s  Sebep" % (genislik_s, "Senaryo", "Beklenen", "Sonuc", "Durum"))
        print("-" * (genislik_s + 55))
        for aciklama, komut, beklenen_s, sonuc_s, durum, sebep in satirlar:
            print("%-*s %-10s %-10s %-6s  %s" % (genislik_s, aciklama, beklenen_s, sonuc_s, durum, sebep))

        print()
        print("Toplam: %d senaryo, %d fark" % (len(satirlar), hata))
        if hata:
            sys.exit(1)
    finally:
        gecici_repo_sil(proje)


if __name__ == "__main__":
    main()
