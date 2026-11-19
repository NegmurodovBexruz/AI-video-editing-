# Serverga o'rnatish: Montaj studiyasi (AP-1077)

Dashboard, agent (Claude Code `claude -p`) va montaj engine bitta Linux konteynerda ishlaydi. HTTPS'ni Caddy beradi. Login bitta superuser bilan, parolni dashboard'dan o'zgartirish mumkin.

```
internet ──443──> caddy (HTTPS, Let's Encrypt) ──> dashboard:8050 (login, API, navbat, agent, ffmpeg, whisper)
                                                   volumes: data (/data), claude_home (/home/app)
```

## 1. Server talablari

| Narsa | Minimum | Nima uchun |
|---|---|---|
| OS | Ubuntu 22.04 / 24.04, x86_64 | Docker image linux/amd64 |
| CPU | 4 yadro (tavsiya 8) | whisper va matting CPU'da ishlaydi |
| RAM | 16 GB | whisper large-v3 va matting eng yuqori nuqtada ~6–8 GB ishlatadi |
| Disk | 100 GB SSD | bitta ish ~200 MB, whisper modeli ~3 GB, image ~3 GB |
| Tarmoq | 80 va 443 portlar ochiq, domen A-yozuvi server IP'siga qaragan | HTTPS sertifikati uchun |
| Dastur | Docker Engine + compose plugin | `curl -fsSL https://get.docker.com \| sh` |

GPU shart emas.

## 2. Kodni serverga olib borish

Team lead'ga `AP-1077-montaj-server-20261116.zip` yuboriladi. ZIP ichida `montaj/`
papkasi, joriy kod, shriftlar va `models/rvm_mobilenetv3_fp32.onnx` bor.
Bu commit qilinmagan oxirgi o'zgarishlarni ham olgan snapshot: `git archive HEAD`
bilan almashtirmang. Eski ishlar, videolar, `.env` va OAuth kiritilmagan.

ZIP'ni serverga yuboring (o'zingizning user/server manzilingizni yozing):

```bash
scp AP-1077-montaj-server-20261116.zip user@SERVER:~/
```

Serverda `unzip` o'rnatilgan bo'lsin. Birinchi o'rnatish:

```bash
sudo mkdir -p /opt
sudo unzip ~/AP-1077-montaj-server-20261116.zip -d /opt
sudo chown -R "$(id -u):$(id -g)" /opt/montaj
cd /opt/montaj
```

Avval `HANDOFF.md` ni o'qing. `PACKAGE_MANIFEST.json` ZIP'dagi payload fayllarining
SHA-256 xeshlarini saqlaydi. Bu source paketi; Docker image serverda yig'iladi.

## 3. Sozlamalar (`.env`)

```bash
cp .env.example .env && nano .env
```

| Kalit | Qiymat |
|---|---|
| `DOMAIN` | masalan `montaj.celion.io` |
| `COOKIE_SECURE` | `1` (HTTPS orqali) |
| `DASH_ADMIN_USER` / `DASH_ADMIN_PASSWORD` | birinchi superuser. Bu qiymatlar faqat birinchi ishga tushishda ishlatiladi; keyin parol dashboard'dagi **"Parol"** tugmasi orqali o'zgartiriladi |
| `MEM_LIMIT` | konteyner RAM chegarasi, masalan `12g` |
| `ANTHROPIC_API_KEY` | Claude API kaliti; faqat `.env` da saqlanadi |

Server uchun yangi admin paroli yarating. `.env.example` dagi `change-me-please`
faqat namuna; uni almashtiring. Haqiqiy `.env` ZIP'da yo'q va git/image'ga kirmaydi.

## 4. Ishga tushirish

```bash
docker compose up -d --build
docker compose ps
docker compose logs --tail=80 dashboard
```

## 5. Claude API'ni ulash

Montaj agenti avvalgidek Claude Code orqali ishlaydi, hisob-kitob esa **API kaliti bilan** qilinadi. Docker'da `DASH_CLAUDE_AUTH=api`: Claude obunasiga `/login` qilish talab qilinmaydi va eski OAuth kirishi API kalitining o'rnini bosmaydi.

```bash
# .env faylini tahrirlab, ANTHROPIC_API_KEY=... qiymatini kiriting.
# Avval navbat bo'shligini tekshiring; so'ng yangi muhit bilan qayta yarating:
docker compose up -d --no-deps --force-recreate dashboard
```

API gateway ishlatilsa, `ANTHROPIC_API_KEY` bo'sh qoladi va `ANTHROPIC_BASE_URL` **hamda** `ANTHROPIC_AUTH_TOKEN` birga beriladi. Faqat URL yozilishi tayyor ulanish hisoblanmaydi.

Kalit yo'q bo'lsa dashboard ochiladi, lekin API kaliti kiritilmagani ko'rsatiladi va haqiqiy agent ishga tushmaydi. `.env` o'zgarganda oddiy `docker compose restart` yangi qiymatlarni olmaydi: konteynerni qayta yaratish kerak. Kalitni Dockerfile, build argumenti yoki git'ga yozmang.

## 6. Higgsfield'ni ulash (bir marta)

Konteyner ishga tushganda `higgsfield` nomli HTTP MCP (`https://mcp.higgsfield.ai/mcp`) user doirasida avtomatik qo'shiladi. Qayta ishga tushish uni takroran qo'shmaydi va mavjud OAuth ma'lumotlarini o'chirmaydi. Bir xil nom boshqa endpoint bilan band bo'lsa, sozlama ustiga yozilmaydi va tushunarli xabar bilan to'xtaydi.

```bash
docker compose exec -it dashboard claude mcp login higgsfield --no-browser
# Terminaldagi havolani brauzerda oching va Higgsfield akkauntiga kiring.
# CLI so'raganda brauzer qaytgan TO'LIQ redirect URL'ni terminalga qo'ying.
docker compose exec dashboard python -I /app/deploy/check_connections.py
```

`--no-browser` Docker va SSH uchun mo'ljallangan: brauzerning localhost callback'i serverga yetmasa ham, manzil satridagi redirect URL'ni terminalga qaytarish mumkin. Qo'shimcha ochiq callback porti talab qilinmaydi. Bu OAuth bosqichi haqiqiy akkaunt bilan hali sinalmagan.

Higgsfield MCP sozlamasi, OAuth ma'lumotlari va agent sessiyalari `claude_home` volume'ida qoladi. Image'ni yangilashda bu volume'ni saqlang (`docker compose down -v` ishlatmang). Claude API kaliti Higgsfield'ga kirish o'rnini bosmaydi.

## 7. Tekshirish

1. `https://DOMAIN` sahifasi login oynasiga yo'naltiradi. Superuser bilan kiring va **"Parol"** tugmasi orqali parolni almashtiring.
2. `docker compose exec dashboard python -I /app/deploy/check_connections.py`: Claude API kaliti sozlanganini va Higgsfield MCP haqiqatan `Connected` ekanini tekshiradi. Model chaqirilmaydi, generatsiya boshlanmaydi, token/kredit sarflanmaydi. Kalitning haqiqiyligi bu tekshiruvda isbotlanmaydi.
3. Dashboard API kaliti yo'qligini noto'g'ri "tayyor" deb ko'rsatmasligi kerak. MCP qo'shilgani OAuth muvaffaqiyatli bo'lganini anglatmaydi.
4. Keyin birinchi qisqa video bilan sinab ko'ring (Minimal, 0 Higgsfield kr; **Claude API tokenlari pullik**). ASR birinchi marta ishlaganda whisper large-v3 modeli yuklanadi (~3 GB, bir marta).

## 8. Yangilash

Avval ishlayotgan **va navbatdagi** ish yo'qligini tekshiring. Dashboard yoki quyidagi
maxfiy qiymat chiqarmaydigan buyruqdan foydalaning (0 bo'lmasa deploy qilmang):

```bash
docker compose exec -T dashboard python -c 'import json,pathlib; active=[p for p in pathlib.Path("/data/jobs").glob("*/job.json") if json.loads(p.read_text()).get("state") in ("running","queued")]; print("Active jobs:",len(active)); raise SystemExit(bool(active))'
```

Backup oling, yangi source'ni joylang, mavjud `.env` va volume'larni saqlang.
Yangilanishni alohida papkadan qilsangiz, eski Compose project nomini `-p` orqali
saqlang; aks holda Compose yangi bo'sh volume yaratishi mumkin. So'ng qayta yig'ing:

```bash
docker compose up -d --build
```

Konteyner qayta yoqilganda agent uzilgan bo'lsa, runner ishni bir marta qayta navbatga qo'yadi
va sessiyani davom ettirishga urinadi. Ikkinchi uzilishda ish "Xato" bo'lib qoladi.
Tiklashga tayanib aktiv ish paytida deploy qilmang; avval navbat bo'shashishini kuting.

## 9. Zaxira nusxa

```bash
docker run --rm -v montaj_data:/data -v "$PWD":/b alpine \
  tar --exclude=./cache -czf /b/montaj-data-$(date +%F).tgz -C /data .
docker run --rm -v montaj_claude_home:/source:ro -v "$PWD":/b alpine \
  tar czf /b/montaj-claude-home-$(date +%F).tgz -C /source .
```

Volume nomlari loyiha papkasi yoki `-p` qiymatidan olinadi: `montaj_data`,
`montaj_claude_home`. Avval `docker volume ls` bilan tekshiring. Backup paytida
navbat bo'sh bo'lsin; undan keyin `docker compose stop dashboard` qilib nusxa oling,
so'ng `docker compose start dashboard`. `.env` ham alohida maxfiy backup qilinadi.
Backup fayllari auth/OAuth va mijoz materiallarini saqlaydi: ommaviy joyga yuklamang.
Whisper cache qayta yuklanishi mumkin; deleted_styles.json ham data backup'iga kiradi.

## 10. Eski ishlarni ko'chirish (ixtiyoriy)

```bash
docker compose cp ./jobs/. dashboard:/data/jobs/
docker compose cp ./companies.json dashboard:/data/companies.json
```

Ish papkalarini PC'dagi `projects\jobs\` dan oldindan nusxalab qo'ying. Ulardagi skriptlar Windows yo'llarini (`D:\…`) saqlaydi; ularni ko'rish va yuklab olish ishlaydi, lekin serverda eski ishni **tuzatish** yangi sessiyada boshlanadi.

## Saqlash muddati va o'chirish

- **Avtomatik tozalash.** Ish oxirgi marta bajarilganidan 14 kun o'tgach (DASH_RETENTION_DAYS) uning videolari serverdan o'chadi: raw, referenslar, render, versiyalar, AI assetlar va ishchi fayllar. Tuzatish yuborilsa, hisob qaytadan boshlanadi.
  - Ishning yozuvi qoladi: nomi, xarajati, "Nima qilindi" ro'yxati va README. Ro'yxatda u "muddati tugadi" deb ko'rinadi.
  - Server buni soatiga bir marta tekshiradi.
  - Ishlab turgan va navbatdagi ishlarga tegilmaydi.
- **Qo'lda o'chirish.** Video sahifasidagi **"Butunlay o'chirish"** tugmasi ish papkasini va agentning Claude sessiya yozuvini serverdan o'chiradi.
  - Tasdiq so'raladi, o'chirilgan ishni qaytarib bo'lmaydi.
  - Ishlab turgan ishni avval to'xtatish kerak.
- **Kartalarda muddat.** Har bir video kartasida "N kun qoldi" yozuvi chiqadi.
- **Uslubni o'chirish.** Katalogdan chiqaradi; eski videolar, montaj va feedback uchun
  assetlar saqlanadi. `/data/deleted_styles.json` Docker restart'da qarorni saqlaydi.

## Bepul dry-run tekshiruvi

Quyidagi alohida konteyner production volume'lariga ulanmaydi. Auth faqat shu
sinov konteynerida o'chiq va port faqat localhost'da. API/generatsiya sarfi yo'q.
Avval production image yig'ilgan bo'lsin (`docker compose build dashboard`).

```bash
docker run -d --name ap1077-smoke -p 127.0.0.1:8051:8050 \
  -e DASH_DRY_RUN=1 -e DASH_AUTH=0 -e DASH_RETENTION_DAYS=0 montaj-studiyasi:latest
docker exec ap1077-smoke python -I /app/dashboard/dev/connections_check.py
docker exec ap1077-smoke python -I /app/dashboard/dev/style_delete_check.py

docker exec ap1077-smoke mkdir -p /tmp/ap1077-media
docker exec ap1077-smoke python -c 'from pathlib import Path; Path("/tmp/ap1077-media/notes.md").write_text("Dry-run test notes\n", encoding="utf-8")'
docker exec ap1077-smoke ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i testsrc2=size=720x1280:rate=30 -f lavfi -i sine=frequency=440:sample_rate=48000 \
  -t 2 -c:v libx264 -preset ultrafast -crf 30 -c:a aac '/tmp/ap1077-media/raw test.mp4'
docker exec ap1077-smoke ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i testsrc2=size=64x64:rate=30 -t 1 -c:v libx264 /tmp/ap1077-media/low.mp4

docker exec ap1077-smoke python -I /app/dashboard/dev/api_check.py http://127.0.0.1:8050 /tmp/ap1077-media
docker exec ap1077-smoke python -I /app/dashboard/dev/feedback_check.py http://127.0.0.1:8050 /tmp/ap1077-media
docker exec ap1077-smoke python -I /app/dashboard/dev/style_check.py http://127.0.0.1:8050 /tmp/ap1077-media
```

Kutiladigan natija: offline testlar `OK`, API/feedback/style testlar `ALL PASS`.
Sinovdan keyin faqat o'zingiz yaratgan `ap1077-smoke` konteynerini to'xtatib o'chiring:

```bash
docker stop ap1077-smoke
docker rm ap1077-smoke
```

Bu real API kaliti, Higgsfield OAuth yoki haqiqiy montaj sifatini isbotlamaydi.

## Cheklovlar (hali yechilmagan)

- **Kredit limitini server majburlamaydi.** Limitni agent o'zi kuzatadi (`HANDOFF.md` §8).
- **Bir vaqtda faqat bitta ish bajariladi.** Navbat RAM tejash uchun shunday qurilgan.
- **429/overloaded holatida faqat bitta qayta urinish bor:** 10 daqiqadan keyin. Bu umumiy retry/backoff tizimi emas.
- **Login faqat bitta foydalanuvchi uchun qilingan.** Kodda foydalanuvchilar ro'yxati bor, lekin yangi foydalanuvchi qo'shadigan UI hali yo'q.
