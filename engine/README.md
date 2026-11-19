# Montaj dvijogi (AP-1077)

Dashbord agenti endi montaj kodini har ishda noldan yozmaydi. Tayyor dvijok qolgan ishni bajaradi. Agentning vazifasi `edit.json` faylini yozish: qaysi ibora, qaysi kalit so'z, qaysi qatlam, qayerda punch va qaysi o'tish. Dvijok shu faylga qarab tahlil, render, ovoz va QA ni o'zi qiladi.

Qoidalar `styles\skills\<uslub>` dagidek. Renderer'da videoning o'ziga xos ma'lumotlari yo'q: o'lchamlar W, H yoki yuz kengligiga (FW) nisbatan beriladi, yuz kengligi esa har kadrda qayta o'lchanadi.

## Holat

| Uslub | Renderer | Sinov |
|---|---|---|
| `in_scene_type` | **tayyor** (`styles\in_scene_type.py`) | iman (720p, 25 fps, yuz kadr kengligining 45 % i) va Sklet (4K, 60 fps, o'zbekcha, kichik yuzli umumiy plan) |
| `talk_ahead`, `pod_glow` | yo'q (keyingi bosqich) | — |
| `brand_stage`, `case_reel`, `spotlight_word` | yo'q (oxirgi bosqich) | — |
| `holo_scene` | yo'q. Namuna kompozitor: `projects\sklet_c053\scripts\compose.py` (Sklet uchun yozilgan, umumlashtirilmagan) | Sklet × SPC, 2026-11-05 |

**Yangi uslublar renderer'i bilan keladi.** "Uslub yaratish" ishida agent `styles\skills\<uslub>\renderer.py` (va `renderer_example.json`) ni ham yozadi. Engine renderer'ni nomi bo'yicha avval `engine\styles\` dan, keyin uslub papkasidan topadi (`core\styles_loader.py`). Shartnoma va tekshiruv: `python -I engine\core\styles_loader.py check <uslub papkasi>`. Dashbord shu tekshiruvdan o'tmagan uslubni ro'yxatga qo'shmaydi.

`analyze.py` (tahlil) hamma uslublar uchun umumiy. Renderer'i hali yo'q uslublar ham undan foydalanadi.

## Ish tartibi

Hammasi `D:\projects\agentic team for editing\.venv\Scripts\python.exe -I` bilan ishga tushiriladi.

```
engine\analyze.py <job> <raw.mp4> [--end S] [--lang uz] [--words transcript.json]
    -> work\meta.json, src30.mp4, speech.wav, cuts.json, words.json, words.txt, matte.mp4, track.json, sheet.png
engine\render.py  <job> --check                      plan tekshiruvi: so'zlar, temp, zoom, glif, xavfsiz zona
engine\render.py  <job> --frames 120,340 --outdir work\qa_frames     alohida kadrlar (PNG)
engine\render.py  <job> --range 300 420 --preview    oraliqni yarim o'lchamda tez ko'rish
engine\render.py  <job> --workers auto               to'liq render: RAM yetsa 2 jarayon -> work\picture.mp4
engine\finish.py  <job>                              ovoz effektlari (uslub qoidasidan), master -14 LUFS / <= -1 dBTP, mux -> out\final.mp4
engine\qa.py      <job>                              sinxron, xavfsiz zona, yuzga yaqinlik, oxirgi kadr, loudness, work\qa_sheet.png
```

`edit.json` formati renderer faylining boshida yozilgan (`styles\in_scene_type.py` docstring). Shu ishga xos qurilma kerak bo'lsa, `"extra": "scripts/devices.py"` bilan ulanadi. U har kadrda `draw(renderer, f, img, matte)` funksiyasini chaqiradi. Dvijok fayllari tahrirlanmaydi.

## O'lchangan tezlik

| | Agent noldan yozgan (iman) | Dvijok (iman) | Dvijok (Sklet, 32 s) |
|---|---|---|---|
| Tahlil | ~11 daq (agent qadamlari bilan) | 2.7 daq | 2.1 daq |
| Bitta to'liq render | 4–7 daq, 3 marta | 2.0 daq (2 jarayon) | 0.9 daq |
| Ovoz va master | bir necha daqiqa | 3 s | 3 s |
| QA | qo'lda, skriptlar yozib | 8 s | 5 s |

Agentning reja yozish vaqti bu jadvalga kirmagan. Undan tashqari, agent endi kompozitor kodini yozmaydi va uni tuzatishga ham vaqt ketmaydi.

## Sinovlarda topilib tuzatilgan narsalar

- **Kesim detektori.** fps aylantirishda takrorlangan kadrlar nol farq berardi va chegara noto'g'ri hisoblanardi. Tuzatildi: iman'da 15 ta kesimning hammasi topiladi. Ulardan bittasini (57.0 s) agent o'zi o'tkazib yuborgan edi.
- **Yuz kuzatuvi.** Haar detektori birlashtirilgan qo'llarni yuz deb olardi. Endi yuz matte'dagi boshga mos kelishi shart.
- **Xavfsiz zona.** Katta so'zlar platformaning o'ng tugmalar ustuniga kirardi. Endi ular 0.86 W dan o'ngga chiqmaydi.
- **Kalit so'zlar.** Iboralar ketma-ket kelganda ikki kalit so'z bir vaqtda ekranda qolardi. Endi har doim faqat bittasi ko'rinadi.
- **Script so'z.** Umumiy planda yuzga tegib turardi. Endi har doim iyakdan pastda turadi.
- **Set-up kesimi.** Tugagan ibora kesimdan keyingi kadrda ham ko'rinib qolardi. Endi kesim bilan birga yo'qoladi.

## Cheklovlar

- Renderer bitta spikerni nazarda tutadi. Kadrda ikki kishi bo'lsa, eng katta yuz kuzatiladi.
- Gesture spawn (qo'ldan chiqadigan raqam) va kiyimdagi logo tayyor emas. Ular `extra` hook orqali qo'shiladi.
- Cellophane overlay berilmasa, procedural zaxira ishlatiladi. U haqiqiy klipdan kuchsizroq chiqadi va bu ogohlantirishda yoziladi.
- QA'dagi platforma zonalari va yuz to'rtburchagi taxminiy. Masalan, iman'dagi 8 ta "yuzga yaqin" ogohlantirish ko'zda tekshirildi: matn bo'yin yonida turibdi, yuzni yopmaydi.
- Caveat va Anton shriftlarida kirill harflari va `ʻ` belgisi yo'q. `--check` buni topadi, shu holda boshqa shrift berish kerak (`"fonts"`).

## Sinov materiallari

`projects\engine_tests\iman` va `projects\engine_tests\sklet` papkalarida `edit.json`, tahlil natijalari va natija videolari bor. Renderer o'zgarganda ikkalasini qayta render qilib, QA ni yana o'tkazing.
