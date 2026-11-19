# Montaj studiyasi: dashbord (AP-1077)

Bu lokal veb-dashbord. Unga referens, raw video va uslub beriladi. Montajni Claude Code (`claude -p`) `styles` plagini va Higgsfield MCP bilan **to'liq mustaqil** qiladi. Tayyor video dashbordda ko'rinadi va shu yerdan yuklab olinadi.

## Ishga tushirish

```
D:\projects\higgsfield test01\dashboard\start.cmd
```
Brauzerda http://127.0.0.1:8050 ochiladi. Dashbord faqat shu kompyuterda ishlaydi, tarmoqdan unga kirib bo'lmaydi. Server faqat Python 3 standart kutubxonasidan foydalanadi, qo'shimcha o'rnatish talab qilinmaydi.

Sinov rejimi: `start-dry-run.cmd`. Bunda Claude Code va Higgsfield o'rniga soxta agent (`dev/fake_agent.py`) ishlaydi, kredit va token sarflanmaydi.

## Qanday ishlaydi

1. Forma mijoz uchun yozilgan va to'rt qismdan iborat:
   - **Videoingiz**: bitta yoki bir nechta raw video, ixtiyoriy nom.
   - **Uslub**: standart holatda "Avtomatik". "Uslubni o'zgartirish" tugmasi ixcham ro'yxatni ochadi: nom va bir qatorli ta'rif (`style_notes.json` dagi `def`). Tanlangandan keyin ro'yxat yana yig'iladi.
   - **Montaj darajasi**: Minimal, Standart yoki Boy (`config.LEVELS`). Har bir darajada kredit va taxminiy dollar ko'rsatiladi. Ixtiyoriy "Sizning limitingiz, $" maydoni ham bor.
   - **Istaklaringiz**: matn, `.md` / `.txt` fayllar va yoqqan videolar.

   **Darajalar va limit:**

   | Daraja | Kredit | Nima kiradi |
   |---|---|---|
   | Minimal | 0 | titr, o'tishlar, grade, ovoz; grafika va AI yo'q |
   | Standart | 10–20 | butun uslub va to'ldirish; faqat AI rasm |
   | Boy | 40–60 | Standart va AI video kadrlar |

   - Agentning limiti daraja maksimumi bilan `$ × 18` ning kichigi (`config.CREDITS_PER_USD`, Higgsfield auto-refill kursi, 2026-11-10).
   - Dollar faqat Higgsfield xarajati: Claude tokenlari va ustama bunga kirmaydi.
   - Tuzatishda mijoz kredit kiritmaydi, ishning daraja limiti (`level_cap`) ishlatiladi.
   - Eski API (`credit_cap` raqam bilan) ham ishlaydi.
2. Har bir ish `projects\jobs\<id>\` papkasiga yoziladi:
   ```
   job.json            sozlamalar va holat (dashbord yozadi)
   input\raw\          raw videolar
   input\refs\         brief.txt (matn), .md/.txt, referens videolar
   AGENT_TASK.md       agentga topshiriq (agent_task.md shablonidan)
   agent.log           Claude Code stream-json logi
   progress.log        agent har bosqichdan keyin yozadigan qisqa qatorlar (o'zbekcha)
   plan.md, gen\, work\  agentning ish fayllari
   out\final.mp4       tayyor video
   README.md           agent hisoboti: qarorlar, kreditlar, ochiq masalalar
   result.json         holat, sarflangan kredit, xulosa
   ```
3. Ishlar navbat bilan bajariladi, bir vaqtda faqat bittasi. Sabab: kompyuterda RAM kam.
4. Uslub va referenslarning vazifasi:
   - Agent avval `styles:<uslub>` skill'ini ochadi va uning ish tartibiga amal qiladi.
   - Referenslar shu uslubni moslash uchun xizmat qiladi: brend, ton, ismlar, faktlar. Ular uslubning o'rnini bosmaydi.
   - Skill'dagi GATE 1 va GATE 2 da agent to'xtamaydi. Foydalanuvchi o'rniga qabul qilgan qarorlarini README'ga yozadi.
   - **Plaginni to'ldirish (faqat shu video uchun).** Video talab qilsa, agent plaginda yo'q element qo'shishi mumkin. Uni boshqa plaginning `references\` qismidan yoki internetdan (WebSearch/WebFetch, faqat umumiy texnikalar) oladi. `styles\` papkasiga hech qachon tegmaydi. Rang, shrift va harakat asosiy uslubdan olinadi, ikkinchi titr tizimi yoki ikkinchi aksent rang qo'shilmaydi. Qo'shimchalar README'ning "Qo'shimchalar" bo'limiga yoziladi. Minimal darajada to'ldirish yo'q.
5. Ish tugagach dashbordda video, **"Nima qilindi"** ro'yxati, README va ochiq masalalar ko'rinadi.
   - "Nima qilindi" — `result.json` dagi `timeline` (`t`, `text`, `quote`) va `overall`.
   - Vaqt bosilsa, video o'sha joyga o'tadi.
   - Video ostida **"O'zgartirish so'rash"** formasi bor (pastdagi bo'limga qarang).

## Tuzatish (feedback) va versiyalar

- **Kimga yuboriladi:** tugagan ishga ("Tayyor", "Xato" yoki "To'xtatilgan" holatidagi).
- **Nima yuboriladi:** matn va ixtiyoriy fayllar: rasm, skrinshot, video, hujjat, musiqa.
- **"⏱ Vaqtni qo'shish":** videoni to'xtatgan joyingiz vaqti izohga yoziladi, masalan `[0:12.4]`.
- **Har bir tuzatishning limiti** ishning daraja limitiga teng. Mijoz uni kiritmaydi. Eski ishlarda, ya'ni darajasiz ishlarda, limit 20.

**Yuborilganda nima bo'ladi:**
1. Joriy natija `versions\v<N>\` papkasiga ko'chiriladi: `final.mp4`, `result.json`, `.srt` va README nusxasi.
2. Izoh va fayllar `feedback\r<N>\` papkasiga saqlanadi.
3. Ish yana navbatga tushadi.

**Agent qanday ishlaydi:**
- Topshiriq `feedback_task.md` shablonidan yasaladi va `feedback\r<N>\TASK.md` ga yoziladi. Unda shunday deyilgan: faqat izohdagi joylarni o'zgartir, qolganini saqla, mavjud `edit.json`, `scripts\`, `work\` fayllaridan foydalan.
- Ishning Claude sessiyasi saqlangan bo'lsa (`~\.claude\projects\D--projects-higgsfield-test01\<id>.jsonl`), agent `--resume` bilan **o'sha suhbatni davom ettiradi**, ya'ni montajni eslab qoladi.
- Sessiya bo'lmasa (masalan, qo'lda import qilingan ish), yangi sessiya ochiladi va agent avval README, `plan.md` va skriptlarni o'qiydi.

**Dashbordda:** versiyalar tugmalar bilan almashtiriladi (v1, v2, …), "Tuzatishlar tarixi" bo'limida har bir izoh va uning fayllari ko'rinadi.

## Yangi uslub yaratish

Chap panelda **"Yangi uslub yaratish"** tugmasi bor.

**Mijoz nima beradi:**
- kamida 2 ta bir xil uslubdagi video;
- ixtiyoriy uslub nomi va "nimasi yoqdi" degan izoh.

**Agent nima qiladi** (topshiriq shabloni: `style_task.md`):
- Videolarni birma-bir, kadrma-kadr (1/30 s) tahlil qiladi. Before/After postlarda faqat After qismini oladi.
- Yangi skill yozadi: `styles\skills\<nom>\SKILL.md` va `references\` dagi 7 ta fayl, `ui_cascade` tuzilmasida.
- **Ikki namuna qoidasi:** Style DNA'ga faqat kamida 2 ta videoda takrorlangan qoidalar kiradi. Bitta videoda ko'rilgan narsa "(1 namunada)" deb ixtiyoriy variant sifatida yoziladi.
- Plaginga faqat o'zgarmas qoidalar yoziladi: bitta videoning raqami, obyekti, brendi yoki matni kirmaydi, muallif nomi ham yozilmaydi. Tugatishdan oldin grep qilinadi.
- Uslub mavjud uslubning takrori bo'lsa, yangi plagin yaratilmaydi. Ish "Xato" bo'lib tugaydi va mijozga mos keladigan mavjud uslub nomi aytiladi.

**Cheklovlar:**
- Higgsfield bu ish uchun `--disallowedTools` bilan yopilgan, xarajat 0 kr.
- Mavjud skill'larga tegish taqiqlangan.
- Tuzatish (feedback) yuborilmaydi.

**Ish tugaganda server tekshiradi** (`store.register_style`):
- nom formati to'g'ri;
- nom yangi (ish boshlanganda `styles_before` ga yozib qo'yilgan ro'yxatda yo'q);
- `SKILL.md` dagi `name` papka nomiga teng;
- 7 ta reference fayli bor;
- `result.json` da `title` va `def` bor.

Hammasi to'g'ri bo'lsa, karta `style_notes.json` ga qo'shiladi va uslub **darhol hamma mijozlar ro'yxatida** paydo bo'ladi.

**Xavf:** uslub hech kim ko'rib chiqmasdan ro'yxatga tushadi, bu foydalanuvchining qarori. Agent mavjud skill papkasini buzsa, server buni faqat nomi bo'yicha ushlaydi. Bunday holatda git'dan qaytariladi.

**Dry-run:** soxta uslublar `projects\jobs_dryrun\_dry_skills\` va `_dry_style_notes.json` ga yoziladi. Haqiqiy plagin va `style_notes.json` ga tegilmaydi, buni `dev\style_check.py` tekshiradi.

## Xavfsizlik va cheklovlar

- **Kredit limiti majburlanmaydi.** Limitni agentning o'zi kuzatadi: topshiriqdagi qat'iy qoidaga ko'ra boshida va oxirida balansni tekshiradi, har bir job'ni ledger'ga yozadi. Dashbord Higgsfield'ga to'g'ridan-to'g'ri ulanmaydi, shuning uchun limitni o'zi to'xtata olmaydi.
- **Higgsfield'da ruxsat etilgan amallar:** faqat generatsiya, yuklash, tahlil, upscale va balans. Nashr qilish, o'chirish, TikTok, akkaunt va billing sozlamalari `--disallowedTools` bilan yopilgan (`runner.py` dagi ro'yxatlar).
- **Agentning yozish huquqi:** fayl tahrirlash `D:\projects\higgsfield test01` ichida avtomatik qabul qilinadi. PowerShell esa ochiq, chunki montajga ffmpeg va Python kerak. Papkadan tashqariga yozmaslik topshiriqda qoida sifatida berilgan, texnik jihatdan to'sib qo'yilmagan.
- **Sub-agentlar o'chirilgan** (RAM sababli).
- **Boshqa saytlardan himoya.** Yozuvchi so'rovlar `X-Dash: 1` sarlavhasini va localhost Host'ini talab qiladi, shuning uchun boshqa sayt brauzer orqali ish boshlay olmaydi.
- **Server qayta ishga tushsa:** davom etayotgan agentga qayta ulanadi. Agent ham to'xtab qolgan bo'lsa, ish "Xato" deb belgilanadi.
- **Sifat haqida:** tuzatishlar bilan natija yaxshilanadi, lekin ideal bo'lishi kafolatlanmaydi. Renderer'i yo'q uslublarda agent kompozitorni qo'lda tahrirlaydi, shuning uchun bitta joyni tuzatayotganda boshqasi o'zgarib qolishi mumkin. Har bir yangi versiyani to'liq ko'rib chiqing.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| `server.py` | HTTP server va API (`/api/styles`, `/api/jobs`, upload, cancel, feedback, video Range) |
| `store.py` | Ish papkalari, yuklash, tuzatishlar va versiyalar, agent loglarini o'qish |
| `runner.py` | Navbat; `claude -p` buyrug'i (tuzatishda `--resume`), ruxsatlar, to'xtatish, qayta ulanish |
| `agent_task.md` | Mustaqil agent uchun topshiriq shabloni |
| `feedback_task.md` | Tuzatish topshirig'i shabloni |
| `style_task.md` | "Yangi uslub yaratish" topshirig'i shabloni |
| `style_notes.json` | Uslub kartalaridagi qisqa o'zbekcha tavsiflar (skill'lar `styles\skills\` dan avtomatik topiladi) |
| `config.py` | Yo'llar, port (`DASH_PORT`), agent Python'i (`DASH_AGENT_PYTHON`), `DASH_DRY_RUN` |
| `static\` | Interfeys (HTML/CSS/JS) |
| `dev\` | Soxta agent va API/lifecycle tekshiruvlari |

Tekshiruv (dry-run server 8051 portda ishlab turganda):
```
python -I dev\api_check.py http://127.0.0.1:8051 <papka: "raw test.mp4" va notes.md>
python -I dev\feedback_check.py http://127.0.0.1:8051 <o'sha papka>
python -I dev\style_check.py http://127.0.0.1:8051 <o'sha papka>
```
