# HANDOFF — Montaj studiyasi / AP-1077

Holat: **2026-11-16**, serverga topshirish uchun kod snapshot'i.
Shu kunning kechki lokal real ishlari, ochiq qarorlar va keyingi qadam: **§9**.
2026-11-17 yangilanishi (qayta yurgizish, uzilgan ishni tiklash): **§10**.
2026-11-17 kech (sifat qoidalari, After Effects rejimi — lokal): **§11**.
2026-11-19 lokal tozalash va qaytarish arxivi: **§12**.

Team lead va keyingi AI agent avval shu faylni, keyin `DEPLOY.md` ni o'qisin.
2026-11-12 tarixiy handoff tashqi lokal arxivga ko'chirilgan (§12): undagi eski
Docker, login, limit va server ko'rsatmalari joriy emas. Kod va ushbu fayl tarixiy hujjatlardan ustun.

## 1. Doira va ishlash qoidalari

- Faqat **AP-1077 — agentic team for editing** ustida ishlang.
- Mahsulot marketing agentligi uchun o'zbekcha web dashboard: raw video,
  referens va istaklardan AI montaj qiladi; natija, QA, xarajat va versiyalar ko'rinadi.
- User qisqa, o'zbekcha (lotin) javob kutadi. Faqat so'ralgan o'zgarishni qiling.
- Rebuild/recreate oldidan queued/running ish yo'qligini tekshiring. Boshqa
  ilova/jarayonlarga tegmang. Mavjud video va ishlarni asrang.
- Haqiqiy API token va Higgsfield generatsiya krediti sarflaydi. Real montaj
  sinovini mas'ul odam ruxsati bilan bajaring. Dry-run token/kredit sarflamaydi.
- Runner bitta ishni bajaradi; subagentlar RAM sabab yopilgan.

## 2. ZIP tarkibi va topshirish holati

- Fayl: `AP-1077-montaj-server-20261116.zip`, ichida bitta `montaj/` papkasi.
- Bu diskdagi **joriy kod**, hali commit qilinmagan oxirgi tuzatishlar ham kiradi.
  `git archive HEAD` eski commitni oladi: oxirgi kod deb ishlatmang.
- Kod, Docker/deploy, 9 ta uslub, shriftlar, ~15 MB RVM ONNX modeli, testlar
  va hujjatlar bor. `PACKAGE_MANIFEST.json` barcha payload fayllar xeshini beradi.
- `.env`, API kalitlari, OAuth/sessiyalar, login bazasi, `.git`, eski videolar,
  ishlar, renderlar, cache, venv va node_modules kiritilmagan.
- ZIP Docker image yoki ma'lumotlar backup'i emas. Server image'ni yig'adi;
  base image/npm/pip va Whisper modelini yuklash uchun internet kerak.
- Lokal Docker tekshirildi: 9 built-in uslub, 0 custom, 0 o'chirilgan uslub, 0 ish.
  Lokal `projects/` dagi tarix boshqa ma'lumot va bu paketga kirmaydi.
- Haqiqiy API kaliti/OAuth bilan to'liq montaj **hali sinalmagan**.
  Mahalliy demo healthy, serverga deploy hali bajarilmagan.

## 3. So'nggi bajarilgan o'zgarishlar

### Limit va referens formasi

- Qo'lda dollar limiti **yoki** Minimal/Standart/Boy tanlanadi: birini kiritish
  ikkinchisini tozalaydi. Darajasiz $5 = floor(5 * 18) = **90 Higgsfield kredit**.
  Daraja maksimumi buni kesmaydi; nol ham yaroqli. Claude xarajati alohida.
- Eski `level + usd_cap` API uchun kichik limit olinishi saqlangan.
- Feedback dastlabki daraja yoki mustaqil dollar limitini saqlaydi.
- Yoqqan video uchun kategoriya yo'q. User o'zi nima yoqqanini yozadi (`ref_like`).
  `ref_use` eski API bilan moslik uchun backend'da qolgan.
- Tanlashdagi ustuvorlik: user so'zlari > referens dalili > plagin DNA > agent didi.

### Claude API va Higgsfield MCP

- Python runner **Claude Code CLI (`claude -p`)** ni ishga tushiradi.
  Bu to'g'ridan-to'g'ri Anthropic SDK integratsiyasi emas: CLI API kaliti bilan ishlaydi.
- Docker `DASH_CLAUDE_AUTH=api`: `ANTHROPIC_API_KEY` yoki gateway uchun
  `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` kerak. Faqat URL yetmaydi.
- **Windows lokal:** `dashboard/start.cmd` aniq `DASH_CLAUDE_AUTH=auto` qo'yadi
  va PC'dagi Claude subscription loginidan foydalanadi (8050). Launcher meros
  gateway/API env'ni faqat o'z jarayonida tozalaydi; global env saqlanadi.
  Login bo'lmasa brauzer orqali kirish talab qilinadi. Saqlangan akkaunt nomi
  yoki faqat MCP OAuth mavjudligi Claude login tayyorligini bildirmaydi.
  Mahalliy Docker demo 8055 esa API rejimida: PC loginini unga ko'chirmang.
- Eski subscription OAuth API kalitining o'rnini bosmaydi. API rejimida child
  muhitidan `CLAUDE_CODE_OAUTH_TOKEN` olib tashlanadi.
- Kalit bo'lmasa dashboard ochiladi, ammo real agent tushunarli xato bilan to'xtaydi.
- `deploy/setup_connections.py` user scope'da `higgsfield` HTTP MCP'ni idempotent
  qo'shadi: `https://mcp.higgsfield.ai/mcp`. Mavjud boshqa endpoint/buzuq config
  ustiga yozmaydi. Ro'yxatdan o'tishi ulanishni isbotlamaydi: OAuth alohida.
- Docker Node 22 ishlatadi; Claude CLI build versiyasi `2.1.322`.
- `deploy/check_connections.py` kalit konfiguratsiyasi va MCP Connected holatini
  tekshiradi; model/generatsiya chaqirmaydi, kalit haqiqiyligini isbotlamaydi.

### Uslub o'chirish

- Har bir katalog kartasida **O'chirish** tugmasi va tasdiqlash oynasi bor.
- `POST /api/styles/<name>/delete`: login + `X-Dash: 1`, idempotent.
- Bu katalogdan o'chirish: asset/notes saqlanadi. Eski video, queued/running
  montaj va feedback buzilmaydi. Yangi video tanlovi/auto ro'yxatidan yo'qoladi.
- Belgilar: real `/data/deleted_styles.json`, dry-run
  `/data/jobs_dryrun/_deleted_styles.json`. Docker restart'da uslub qaytmaydi.
- O'chirilgan uslub bilan yangi create va eski draft submit rad etiladi;
  tugagan ishga feedback mumkin. Nomlar band qoladi: yangi uslub eski assetni almashtirmaydi.
- Tiklash UI'si yoki assetlarni butunlay tozalash hozir yo'q.

## 4. Kod xaritasi

| Joy | Vazifasi |
|---|---|
| `dashboard/server.py` | API, auth, upload, static va video range |
| `dashboard/store.py` | Diskdagi ishlar, uslublar, limit, kompaniya, feedback, retention |
| `dashboard/config.py` | Env/yo'llar, formatlar va limitlar |
| `dashboard/runner.py` | Ketma-ket worker, Claude buyruqlari, task, QA, health |
| `dashboard/connections.py` | Maxfiy qiymatsiz auth/MCP readiness |
| `dashboard/static/` | Frameworksiz HTML/CSS/JS; Node frontend build yo'q |
| `dashboard/agent_task.md`, `feedback_task.md`, `style_task.md` | Agent task shablonlari |
| `dashboard/dev/` | Fake agent va testlar |
| `engine/` | Analyze/render/finish/QA, reference tahlili |
| `ae_mcp/` | After Effects MCP server (faqat Windows, AE o'rnatilgan PC; §11) |
| `engine/fonts/`, `assets/*.ttf` | Lokal shriftlar |
| `models/rvm_mobilenetv3_fp32.onnx` | Paketga kiritilgan matte modeli |
| `styles/.claude-plugin/`, `styles/skills/`, `styles/docs/` | CLI plagini va 9 ta uslub |
| `scripts/` | Eski compositor yordamchilari; ayrimlari tarixiy media talab qiladi |
| `refs/ref_ba_20261109/analysis.md` | Style agent uchun matnli namuna, asl media yo'q |
| `deploy/`, `Dockerfile`, `docker-compose.yml` | Linux image, MCP setup va Caddy HTTPS |

`in_scene_type` uchun umumiy renderer bor. Hamma 9 uslubda tayyor renderer bor
deb taxmin qilmang: boshqalarda job compositor ishlatilishi mumkin. Yangi uslub
kamida 2 ta referens, `renderer.py`, `renderer_example.json` va 7 reference hujjat
bilan keladi; `engine/core/styles_loader.py check` dan o'tishi kerak.

## 5. Server ma'lumotlari va yangilash

- Kod `/app`; Linux yo'llari env'dan olinadi. Eski README'dagi `D:\...` server buyrug'i emas.
- `data` volume -> `/data`: jobs, companies.json, auth, styles,
  style_notes_custom.json, deleted_styles.json, cache.
- `claude_home` -> `/home/app`: MCP/OAuth va agent sessiyalari.
  Caddy uchun `caddy_data` va `caddy_config` ham saqlanadi.
- `docker compose down -v` ma'lumotlarni yo'qotadi. Yangilashda volume'larni asrang.
- Entrypoint built-in uslublarni image'dan yangilaydi, custom uslublarni saqlaydi;
  shu sabab o'chirish alohida JSON bilan boshqariladi.
- Server retention standarti 14 kun: media/renderlar tozalanadi, yozuv/README qoladi.
  `DASH_RETENTION_DAYS=0` avtomatik tozalashni o'chiradi.
- Kompaniya arxivlanadi. Video ishini butunlay o'chirish boshqa API/UI bilan bor;
  running ish avval to'xtatiladi. Uslub o'chirish assetni butunlay yo'qotish emas.

## 6. Team lead birinchi nima qiladi?

1. ZIP'ni `/opt` ga oching: `/opt/montaj`. `DEPLOY.md` bo'yicha server/domen tayyorlang.
2. `.env.example` -> `.env`; domen, yangi admin paroli va Claude API kalitini kiriting.
   ZIP'da real parol/token yo'q. Placeholder parolni ishlatmang.
3. `docker compose config --quiet`, so'ng `docker compose up -d --build`.
4. HTTPS/login'ni tekshiring; Higgsfield OAuth komandasi `DEPLOY.md` da.
5. `deploy/check_connections.py` ni ishlating. Real kalit va OAuth hali sinalmagan:
   konfiguratsiya borligini to'liq montaj muvaffaqiyati deb belgilamang.
6. Ruxsat bilan qisqa Minimal videoni oxirigacha o'tkazing, natija/QA/feedback'ni tekshiring.
   Minimalda Higgsfield 0 kr, ammo Claude API tokenlari pullik.
7. Backup va retention sozlamalarini tekshiring. Production'ga umumiy dev testlarni yubormang.

## 7. Tekshiruvlar va davom ettirish

2026-11-16 da bajarilgan tekshiruvlar:

- `connections_check.py`: 11 offline test, Windows/Linux.
- `style_delete_check.py`: 7 izolyatsiyalangan test, Windows/Linux.
- Dry-run API, feedback, referens va style yaratish testlari.
- Desktop/mobile: limit almashuvi, ref_like, delete confirm/cancel, error/retry,
  loading, draft reset va reload persistence; JS xatosi yo'q.
- Mahalliy Docker demo `http://127.0.0.1:8055/`, healthy. Bu team lead serveri emas.
  Haqiqiy user uslubi sinov uchun o'chirilmagan.

ZIP'dan mustaqil test buyruqlari `DEPLOY.md` dagi **Bepul dry-run tekshiruvi** bo'limida.
Test media arxivda yo'q: ffmpeg bilan sun'iy yaratiladi. Whisper katta modeli ham
arxivda yo'q: birinchi ASR'da yuklanadi va cache'da qoladi.

Agent davom ettirganda env/volume/kod holatini tekshirsin, maxfiy qiymatni
logga chiqarmasin, active job'ni buzmasin. ZIP'da `.git` yo'q: yangi repo'ga import
qilish mumkin; eski commit mavjud yoki barcha tuzatishlar commit qilingan deb taxmin qilmang.
`dashboard/README.md`, `engine/README.md` va tarixiy handoff'da eski misollar bor;
joriy auth/limit/deploy holati uchun shu fayl, `DEPLOY.md` va kodga qarang.

## 8. Ma'lum cheklovlar

- Kredit limitini server billing darajasida majburlamaydi; agent kuzatadi.
  Umumiy job timeout yo'q. UI hisob-kitobi billing kafolati emas.
- 429 uchun maxsus retry/backoff yo'q.
- Dashboard balansi tugagan ishlar hisobotidan olinadi; live emas, eskirishi mumkin.
- Bitta admin ishlatishiga moslangan; multi-user boshqaruv UI'si yo'q.
- Headless MCP OAuth komandasi CLI help'da bor, lekin masofaviy haqiqiy akkaunt
  OAuth jarayoni va API bilan to'liq montaj hali tekshirilmagan.
- Eski compositor'lar tarixiy media/absolyut yo'llarga bog'langan bo'lishi mumkin.
  Ular standalone demo emas; joriy runner/engine yangi job papkasida ishlaydi.
- Video oxiri muzlamasin, audio odatda -14 LUFS. Pishirilgan grafika/matnni
  olib tashlash agentni uzoq tuzatish sikliga olib kelishi mumkin.
- Billing enforcement, timeout, boshqa render framework'lari tarixda taklif
  qilingan, ammo bajarilgan yoki yangi tasdiqlangan ish emas. Scope'ni kengaytirmang.

## 9. 2026-11-16 kech: lokal real montajlar (8050)

Bugun lokal dashboardda (`dashboard/start.cmd`, PC subscription login) birinchi marta
**real montajlar oxirigacha muvaffaqiyatli o'tdi**. Bu §2/§6 dagi "real yo'l sinalmagan"
gapini faqat **lokal** uchun yopadi; server/API kalit rejimi hali sinalmagan.

### "Savol" seriyasi (agro, pH/o'g'it, 9:16, Boy 60 kr, kompaniyasiz)

| Ish | Raw | Referens | Natija |
|---|---|---|---|
| `261116-115429-auto-18c9` | савол 2 | `yi4DYZ5UNzkl9g.mp4` + brief | **failed**: birinchi so'rovda 429 (subscription limiti, ~12 ta `claude` jarayoni ochiq edi), 0 kr |
| `261116-121052-auto-bb51` | савол 2 | xuddi shu (qayta yurgizish) | done, `custom:soil_infodeck`, 2 ta tuzatish (r1 titrlar, r2 AI lavhalar juda tez) |
| `261116-151837-auto-be6c` | савол 3 | bb51 natijasi `final (3).mp4` + brief | done, 31 kr |
| `261116-160625-auto-f0eb` | савол 4 | be6c natijasi + brief (agent yozgan, user brief'i yo'q edi) | done, 41.75 kr, 42.5 s, QA 13/13 |
| `261116-162120-auto-616b` | савол 5 | `final (4).mp4` + brief | done, 39.75 kr (user o'zi boshlagan) |
| `261116-160625-newstyle-0586` | — | final (3), be6c natijasi, style_card | **cancelled** (user to'xtatdi): seriya uslubi plagin bo'lmadi |

- Seriya zanjiri: har keyingi savol oldingi natija videosini referens qilib oladi
  (`style_source: reference`). Bu ishlayapti, ammo plaginsiz: har safar referens tahlili qaytadan.
- Raw videolar oldin montaj qilingan (kuydirilgan titr 925–1480 px, eski musiqa/SFX):
  agent ularni qorong'i panel bilan yopadi. Toza raw bo'lsa panel kerak emas.
- 616b hisobotida: balans 151.75 kr kamaygan, shundan 112 kr shu akkauntdagi boshqa
  sessiyaning Genjutsu to'lovlari. Dashboard balansi akkaunt bo'yicha, ish bo'yicha emas.

### Bugun aniqlangan bo'shliqlar (kod o'zgartirilmagan)

1. **Failed ishni qayta yurgizish UI'si yo'q** (`store.submit` faqat `draft`). 429 bo'lsa
   user formani qaytadan to'ldiradi. Vaqtincha yo'l: dashboard `store` kodi bilan yangi
   ish yaratib navbatga qo'yish; ishlab turgan server diskdan oladi (lokal API login so'raydi).
   Skriptlar: `C:\Users\bexru\.claude\scratch_ap1077\requeue_18c9.py`, `queue_savol4.py`.
2. **429 retry/backoff yo'q** (§8). Subscription rejimida boshqa ochiq Claude sessiyalari
   limitni bo'lishadi.
3. **Feedback'dan o'rganish yo'q.** Feedback faqat o'sha ishning tuzatishiga ketadi
   (`feedback_task.md`, `--resume`). Yangi ish oldingi izohlarni ko'rmaydi.
   Nazoratsiz istisno: headless agentlar Claude Code auto-memory yozmoqda
   (`C:\Users\bexru\.claude\projects\D--projects-higgsfield-test01\memory\`, 3 yozuv:
   PowerShell `python -c` qo'shtirnoq, `get_preferences` rad etiladi, raw'da kuydirilgan grafika).
   Docker'da bu `/home/app` ostida alohida, noldan boshlanadi.

### Ochiq qaror: "Saboqlar" qatlami (taklif, user tasdiqlamagan)

- Tuzatish agenti `lessons.json` nomzodlarini yozadi (qoida + qamrov + dalil, videoga xos px/vaqt yo'q),
  dashboardda "Saboqlar" bo'limi: tasdiqlash/tahrirlash/rad etish, `/data/lessons.json`.
- Runner faqat tasdiqlanganlarni `AGENT_TASK.md` ga qo'shadi (umumiy + uslub + kompaniya, ≤ ~15).
  Ustuvorlik: joriy user so'zlari > referens > saboqlar > plagin DNA > agent didi.
- Qamrov: **umumiy** = faqat sifat/o'qilish qoidalari; **uslub**; **kompaniya** = did (shubhada shu);
  kompaniyasiz ishdan did-saboq yozilmaydi.
- Job agentlari uchun auto-memory o'chirilsin, foydali texnik tuzoqlar `agent_task.md` ga ko'chsin.
  O'chiruvchi aniq env/sozlama nomi hali tekshirilmagan.
- **Userdan javob kutilmoqda:** (a) saboqlar tasdiqdan keyinmi yoki avtomatik (tavsiya: tasdiq);
  (b) feedback'ni kim yozadi — agentlik xodimi (uy uslubi → umumiy) yoki mijoz (→ kompaniya).
- Hozirgacha real feedback: 4 ta izoh, 3 ishda (8103, 4aa1, bb51 r1/r2). Umumiy qoida uchun kam.

### Keyingi qadam

1. Seriya uslubini plagin qilish kerakmi — user 0586 ni to'xtatgan, sababini so'rang;
   kerak bo'lsa be6c yoki f0eb dan "Shu uslubni saqlash" bilan qayta.
2. Saboqlar qatlami bo'yicha (a)/(b) javobidan keyin implement + dry-run testlar.
3. Diskdagi o'zgarishlar hali commit qilinmagan (oxirgi commit `cdc290b`, 11-12).

## 10. 2026-11-17: qayta yurgizish va uzilgan ishni tiklash

Sabab: lokal dashboard RAM tanqisligida o'ldirildi, f9cc ishining tuzatish 2 si `running` holatida
qotib qoldi; server qayta yonganda `failed` bo'ldi va izohni qo'lda qayta yuborish kerak bo'ldi.
§9 dagi 1- va 2-bo'shliq shu bilan yopildi (429 uchun bitta kechiktirilgan urinish).

- **"Qayta yurgizish" tugmasi** (`POST /api/jobs/<id>/retry`, `store.retry_job`):
  - xato bilan tugagan birinchi yurish: xuddi shu input/ va sozlamalar bilan **yangi ish** ochiladi
    (yangi papka, yangi Claude sessiyasi); eskisi yozuv bo'lib qoladi, `retried_as` / `retry_of` bog'lanadi,
    ikkinchi marta bosish rad etiladi;
  - xato bilan tugagan tuzatish: o'sha izoh va fayllar **shu ishning** keyingi tuzatishi sifatida qayta yuboriladi,
    oldingi versiyalar saqlanadi.
- **Avtomatik tiklash** (`runner.auto_requeue`), har yurish uchun **faqat 1 marta** (`auto_retries`):
  - server qayta yonganda agenti o'lgan ish `failed` emas, qayta navbatga qo'yiladi (tuzatish raqami saqlanadi);
  - Claude 429 / overloaded bo'lsa, 10 daqiqadan keyin bir marta qayta (`not_before`, `next_queued` kutadi);
  - qayta yurishda agent o'z sessiyasini davom ettiradi (`--resume`, birinchi yurishda ham) va
    "to'xtagan joydan davom et, bor assetlarni qayta generatsiya qilma" degan izoh oladi;
  - agentning o'z `failed` xulosasi yoki user to'xtatgan ish qayta yurgizilmaydi; ikkinchi uzilish `failed` qoladi;
  - yangi tuzatish yuborilganda hisoblagich nolga tushadi.
- **`start.cmd`** server to'xtasa 5 s dan keyin uni qayta yoqadi (oynani yopish = to'xtatish). Lokal serverni
  Claude Code fon vazifasi sifatida emas, alohida oynada ishga tushiring: fon vazifasini sessiya xotira
  tanqisligida o'ldiradi. Docker'da buni `restart` siyosati bajaradi.
- `connections.claude_auth`: `.credentials.json` da faqat MCP OAuth bo'lsa, Claude login bor deb hisoblanmaydi.
- Testlar: `dev/retry_check.py` (9), `dev/autoretry_check.py` (7); `connections_check`, `style_delete_check`,
  dry-run `api_check`, `feedback_check` o'tdi. Dry-run'da server+agent o'ldirilib qayta yoqildi: ish o'zi
  qayta navbatga tushdi va `done` bo'ldi.
- Ma'lum cheklov: qayta urinishda kredit limiti yana to'liq beriladi (server sarfni majburlamaydi, agent
  sessiyadan eslaydi). Real pullik ishda avtomatik tiklash hali sinalmagan.

## 11. 2026-11-17 kech: sifat qoidalari va After Effects rejimi (lokal)

Sabab: user "feedback'larni to'g'ri qilyapti, lekin montajni odamlardek qilolmayapti" dedi. f9cc kontakt varag'ida
ko'ringan muammolar: 6–7 xil karta uslubi aralash, bo'sh karta va panjara, chetdan kesilgan sarlavha, AI kadrlar
rangi boshlovchi kadriga mos emas, stikerga o'xshash uchuvchi nonlar. f9cc da 77 s ga 32 ta hodisa bo'lgan, eski QA OK degan.

### Sifat qoidalari (`agent_task.md` → "Quality", `engine/qa_check.py` → `c_restraint`)
- **Bitta dizayn tili:** 1 xil titr tizimi, ko'pi bilan 2 xil karta, karta va grafika birga 3 xil. Ular **necha marta**
  chiqishi cheklanmaydi: zich montaj mumkin.
- **Chala narsa yo'q:** bo'sh karta yoki panjara, chetdan kesilgan matn (≤ 0.5 s o'tishdan tashqari), kliparat stikerlar bo'lmaydi.
- **AI kadrlar** boshlovchi videosining rangiga moslanadi (LAB'da Reinhard rang ko'chirish, kuchi 0.5–0.7). Topshirishdan oldin agent
  har 2 s dan kontakt varaq olib o'zi tekshiradi.
- **QA:** agent `work/records.json` ga `devices` ro'yxatini yozadi (`kind`, `group` = caption | card | graphic | insert,
  `t`, `asked`). Turlar chegaradan oshsa FAIL, birinchi yurishda ro'yxat yo'q bo'lsa ham FAIL. Tuzatishda faqat WARN,
  chunki u yerda user izohlari ustun. `asked: true` (userning o'zi so'ragan element) hisobga kirmaydi.
  Minimal darajada `devices` bo'lsa FAIL.
- **User qarori:** effektlar **sonini** cheklash (har 12 s ga 1, 40 % toza kadr) bir marta qo'shilgan edi, user
  rad etdi ("kuchli effektlar kam deganing yoqmadi"), olib tashlandi. Reels janri zich: muammo son emas, sifat.
  Qaytarmang.
- Testlar: `dev/restraint_check.py` (8). Soxta agent ham `devices` yozadi.

### After Effects rejimi (`ae_mcp/`, faqat shu Windows PC)
- `ae_mcp/server.py`: MCP stdio server (faqat stdlib), uchta asbob: `ae_run` (ExtendScript + `lib.jsx` yordamchilari,
  `<job>/ae/project.aep`), `ae_frames` (PNG kadrlar, `saveFrameToPng`), `ae_render` (`aerender` → H.264 mp4 yoki
  alpha ProRes 4444 mov). Har chaqiruvda yangi AE `-noui` jarayoni ochiladi, loyiha fayli holatni saqlaydi.
  Tafsilot va tuzoqlar `ae_mcp/README.md` da.
- **Himoya:** faqat `AE_MCP_ROOTS` (dashboard jobs papkasi) ichida ishlaydi. Bir vaqtda bitta AE ishlaydi. User ochgan AE ga
  tegilmaydi. Bo'sh RAM kamida 3 GB bo'lishi kerak. Timeout bor.
- **Dashboard:** `config.AE_ENABLED` AE o'rnatilgan Windows'da avtomatik yoqiladi, `DASH_AE=0` o'chiradi. Linux/Docker
  (VM3) da AE yo'q, rejim o'chiq. `runner.build_cmd` `work/ae_mcp.json` + `--mcp-config` va `mcp__ae__*`
  ruxsatlarini qo'shadi (uslub yaratish ishlarida qo'shilmaydi). Topshiriqda "After Effects" bo'limi bor: har bir effekt
  alohida comp va alpha render qilinadi, montaj ustiga qo'yiladi, butun video AE dan o'tkazilmaydi, renderdan oldin `ae_frames` ishlatiladi.
- **Tuzoq:** `app.newProject()` AE 2025 ni `-noui` da qulatadi (`0xC0000409`). Server AE ochgan bo'sh loyihadan
  foydalanadi. PNG sequence shabloni yo'q.
- **Tekshirilgan:** jonli smoke test o'tdi (yaratish, qayta ochish, xato qatori, yo'l chegarasi, 4 kadr, mp4 va alpha
  mov). Headless `claude -p --mcp-config` `ae_run` ni chaqirib natija oldi (haiku, $0.006). Testlar:
  `dev/ae_mcp_check.py` (10). **AE bilan to'liq real montaj hali sinalmagan.**
- **Ochiq masalalar:**
  - Adobe litsenziyasi desktop AE ni mijozlar uchun avtomatik xizmatda ishlatishga ruxsat beradimi, tekshirilmagan.
  - 15 GB RAM: AE + boshqa og'ir qadamlar bir vaqtda bo'lmasin.
  - Uslub shriftlari AE da o'rnatilganmi, har job da `FONT MISMATCH` log orqali ko'rinadi.

### Keyingi qadam
1. Ruxsat bilan AE rejimida qisqa real montaj o'tkazib, f9cc dagi effektlar bilan yonma-yon solishtirish.
2. "Saboqlar" qatlami (§9). Bu Managed Agents "Dreams" g'oyasining lokal varianti: Dreams o'zi bizga mos emas, chunki faqat
   bulutdagi Managed Agents sessiyalari bilan ishlaydi. Userdan (a)/(b) javoblari hali kutilmoqda.

## 12. 2026-11-19: lokal tozalash

- Eski dashboard nusxasi (`dashboard/_codex_version_20261106`), amalga oshirilgan dizayn qoralamalari
  (`dashboard/design`), tarixiy handoff (`docs`), `projects/codex_checks`, eski `projects/jobs_dryrun`,
  `dashboard/dev/*.log` va 7 ta `__pycache__` papkasi loyiha tashqarisiga arxivlandi: jami 440 fayl.
- Qaytarish arxivi: `D:\projects\AP-1077-cleanup-20261119`. `files/` ichida asl nisbiy yo'llar,
  `cleanup-manifest.json` da fayllar ro'yxati va SHA-256 xeshlari, `README.md` da qaytarish tartibi bor.
  Bu lokal arxiv, server paketi tarkibiga kirmaydi. Fayllar o'chirilmagan; disk joyi bo'shatilgani emas.
- Haqiqiy montajlar, videolar, referenslar, uslublar, shriftlar, model, login/sozlamalar va
  `projects/engine_tests` saqlandi. Eski test natijalari va Python cache'lari `.gitignore` bilan chiqarildi.
- Tekshiruv: qolgan 2773 faylning hajmi/vaqti saqlandi, arxivdagi 440 fayl xeshi mos;
  retry/autoretry 16 testi o'tdi, 9 uslub katalogda bor, server paketi payload tekshiruvi o'tdi.

## 13. 2026-11-19: GitHub uchun source nusxasi

- Repository: `https://github.com/NegmurodovBexruz/AI-video-editing-`, nashr tarmog'i `main`.
- Nashr checkout'i: `D:\projects\AP-1077-github-publish`, lokal branch `ap1077/github-publish`.
  U GitHub'dagi boshlang'ich commitdan ajratilgan; eski lokal `main` tarixi va undagi mijoz/job yozuvlari
  GitHub'ga yuboriladigan branch ajdodlari emas. Asosiy lokal ish papkasi o'z tarixini saqlaydi.
- Joriy kod `deploy/package_release.py` payload ro'yxati orqali shu checkout'ga ko'chiriladi.
  Keyingi nashrda ham source'ni tekshirib sinxronlang; eski lokal `main`ni bevosita push qilmang.
- To'liq README: arxitektura, imkoniyatlar, Windows/Docker, auth, darajalar, uslublar, AE, testlar va cheklovlar.
- `.gitignore` lokal ish/media va auth ma'lumotlarini chiqaradi; RVM modeli aniq istisno bilan kiritiladi.
  Model upstream v1.0.0 bilan SHA-256 bo'yicha mos. U va shriftlarning litsenziya matnlari `third_party/`da.
- Paketlashga yetishmayotgan `deploy/Caddyfile`, AE server/JSX, MIT LICENSE va asset litsenziyalari qo'shildi.
- Toza checkout tekshiruvi: 53 offline test, 50 Python fayli sintaksisi, 24 README havolasi,
  Compose config va ZIP integrity o'tdi. Real montaj yoki pullik API chaqiruvi bajarilmadi.
