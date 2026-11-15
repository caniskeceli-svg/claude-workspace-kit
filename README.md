# claude-workspace-kit

Can İskeçeli'nin tüm projelerinde ortak kullandığı Claude Code "yönetişim" kiti:
genel çalışma kuralları, şüpheci bir denetçi alt ajanı ve fiziksel silmeyi
engelleyip karantinaya yönlendiren bir PreToolUse hook'u.

## İçindekiler

| Dosya | Hedefte nereye gider |
|---|---|
| `CLAUDE.general.md` | `CLAUDE.md`'nin başına eklenir (repoya özel içerik korunur) |
| `denetci.md` | `.claude/agents/denetci.md` |
| `silme_kilidi.py` | `.claude/hooks/silme_kilidi.py` |
| `settings.fragment.json` | `.claude/settings.json`'a merge edilir |
| `merge_kurulum.py` | `install.sh`'in kullandığı yardımcı (kopyalanmaz) |
| `test_silme_kilidi.py` | Hook'un karar mantığını 40 senaryoyla doğrular (gerçek silme yapmaz) |

## Kurulum (yeni/mevcut bir repoya)

```bash
# 1) Bu kiti klonla (ya da zaten klonluysa güncelle)
git clone https://github.com/caniskeceli-svg/claude-workspace-kit.git
cd claude-workspace-kit

# 2) Hedef repoya kur
./install.sh /path/to/hedef-repo
```

`install.sh`:
- `denetci.md` ve `silme_kilidi.py`'yi kopyalar.
- `CLAUDE.md`'nin başına genel kurallar bölümünü ekler — repoya özel içerik **asla silinmez**; script tekrar çalıştırılırsa aynı bölümü yerinde günceller (idempotent, marker: `<!-- claude-workspace-kit:start/end -->`).
- `.claude/settings.json`'a hook girdisini **merge** eder; var olan başka hook'lara dokunmaz.

Tek bağımlılık: `python3` (hook ve merge script'i için) ve `bash`.

## `silme_kilidi.py` ne yapar

Her `Bash` araç çağrısından önce çalışır (PreToolUse). Komutu `shlex` ile
ayrıştırır (tırnak içini korur, `bash -c "..."` gibi iç kabukları da açar),
ve şu öncelik sırasıyla karar verir:

1. **Gizli dosya** (`.env*`, `*.key`, `*.pem`, `secrets*`) → her zaman engelli.
2. **Repo dışı hedef** → engelli.
3. **Junk/derleme çıktısı** (`__pycache__`, `.pytest_cache`, `node_modules`,
   `dist`, `build`, `.cache`, `*.pyc`) repo içindeyse → serbest.
4. **git-takipli** dosya/dizin (repo içinde) → serbest (geri gelir).
5. Diğer her silme (takipsiz, junk değil) → **engelli**, karantina önerilir.
6. `git push --force`/`--force-with-lease`, `git clean`, `git reset --hard`,
   `git branch -D`, uzak branch silme → **her zaman engelli** (git-takipli
   olsa bile — bunlar tek dosya silme değil, repo geçmişini/durumunu bozan
   işlemler).
7. `find -delete` / `find -exec rm`, `rsync --delete` → **her zaman engelli**
   (hedefleri dinamik, güvenli değerlendirilemez).

Ayrıştırma başarısız olursa ya da belirsizse **fail-closed**: engeller.

## Test

```bash
python3 test_silme_kilidi.py
```

40 senaryoyu (engellenmesi ve geçmesi gerekenler) doğrudan karar
fonksiyonuna (`degerlendir()`) sorar — gerçek dosya silmez. Gerçek hook
protokolünü (stdin JSON → exit code) doğrulamak için:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' \
  | CLAUDE_PROJECT_DIR=/path/to/repo python3 silme_kilidi.py; echo "exit=$?"   # 2 beklenir
```

## Bilinen sınırlamalar

- `rm` hedefinin göreli yolu, Bash aracının **o anki çalışma dizinine** göre
  değil, `$CLAUDE_PROJECT_DIR`'e göre çözülür (hook, komutun gerçek `cwd`'sini
  bilemez). Proje kökünden uzakta `cd` yapılmışsa yanlış değerlendirebilir.
- `xargs rm` gibi dolaylı çağrılar (hedef, `rm`'in kendi argümanı değil,
  başka bir programın ürettiği girdi) yakalanmaz.
- Bu bir **sondan güvenlik ağı**dır, tek koruma katmanı olarak güvenilmemeli;
  asıl disiplin `CLAUDE.general.md`'deki "silme yok, karantinaya taşı" kuralı.
