# Before/After juftligi: After qismining tahlili (2026-11-09)

AP-1077. Manba: `Downloads\Telegram Desktop\NU8AkbgyU2NP6w.mp4` (17.4 s) va `BUUK0FIw2GRipQ.mp4` (15.7 s). Ikkalasi ham bitta montajchining portfolio posti. Fonda shahar fotosi, chapda kichik "Before" oynasi, o'ngda katta "After" oynasi, pastda dastur ikonkalari paneli.

Foydalanuvchi qoidasi: **faqat After qismi tahlil qilinadi**, post qobig'i uslubga kirmaydi.

Hujjatdagi atamalar:
- **v1:** NU8AkbgyU2NP6w;
- **v2:** BUUK0FIw2GRipQ;
- **H, W:** After kadrining balandligi va kengligi;
- **f:** kadr raqami, 1 kadr = 1/30 s.

## Ish fayllari

**After qismini kesib olish:**
- oyna sarlavhasidagi qizil nuqta ikkala videoda ham (274, 140) da, oyna qimirlamaydi;
- After video 9:16 nisbatda: `crop=432:768:250:134`;
- uning yuqori ~26 pikselini (0.034 H) oyna sarlavhasi yopadi.

**Fayllar** (`<id>\` papkada):

| Fayl | Mazmuni |
|---|---|
| `after.mp4` | kesib olingan After video, ovozi bilan |
| `after_sheet_025s.jpg` | 0.25 s qadamli kadrlar varag'i |
| `overview_05s.jpg` | butun post, 0.5 s qadam |
| `strips\*.jpg` | har bir kadr (1/30 s), kadr raqami bilan |
| `transcript.json` | faster-whisper large-v3, ru, so'z vaqtlari |
| `motion_std.png` | oyna chegarasini topish uchun harakat xaritasi |

**Ovoz o'lchovi:**
- integrated: v1 −15.6 LUFS, v2 −20.8 LUFS;
- LRA 2.8 / 2.3 LU.

Bu yuklangan postning ovozi, shuning uchun plagin qoidasi emas.

## Tuzilish

**v1** (setup 4 marta almashadi, ko'cha, bitta spiker, nutq uzluksiz):

| s | Nutq vazifasi | Qurilma |
|---|---|---|
| 0–3.6 | Hook va raqam diapazoni | Harflab yig'iladigan stack: 2 ta katta oq so'z, kichik "ty v", magenta kalit so'z, kulrang bog'lovchi so'z, `[qavsdagi]` so'z. Raqamlar uchun magenta **plashka**: chapdan o'sadi, ustiga oq raqam, ostida kichik magenta teg |
| 3.6–7.3 | Ro'yxat: nimalarga pul yetadi | Setup kesimi. Stack yoziladi. Har bir sanalgan narsaga **3D yaltiroq binafsha romb ikonka** chiqadi, ular bosh tepasida romb panjara bo'lib yig'iladi (3 ta) |
| 7.3 | Setup kesimi | **Negativ-flash**: oq bloom kadr → 3 ta negativ kadr → oq kadr |
| 7.3–10.3 | Taqqoslash | Kulrang, yarim shaffof katta so'z va uning atrofida kichik qatorlar stack'i |
| 10.3 | Setup kesimi | Negativ-flash |
| 10.4–13.6 | "Hammasi joyida" | Tepada katta magenta KATTA HARFLI sarlavha: harflab chiqadi va **asta chapga suriladi**. Ostida `[qavs]` qator (bosh orqasida qoladi). Ko'krakda katta oq **bosh harf** (drop-cap), yonida kichik 2 qator, ostida magenta qator |
| 13.7 | Setup kesimi | Oddiy kesim |
| 13.7–17.4 | Xulosa | Kichik markazlashgan qatorlar, bitta katta oq so'z (stack). 15.25 da yana negativ-flash |

**v2** (studiya, mikrofon, bitta spiker):

| s | Nutq vazifasi | Qurilma |
|---|---|---|
| 0–2.4 | "Kontent qildik, ko'rishlar nol" | So'zma-so'z oq qator. Pastdan **shisha video kartalar yelpig'ichi** ko'tariladi: binafsha, thumbnail, ko'rish hisoblagichi. Qizil teg va hisoblagich "0" gacha tushadi |
| 2.45, 3.45 | Urg'u | **Bloom-glitch flash**: kadr oq yonadi, matn chiziqlarga cho'ziladi, 1 negativ kadr |
| 2.6–4.6 | "Muammo kamerada emas, montajda" | Qator yig'iladi, magenta tagli so'z. Dastur ikonkasi 3D shishada aylanib chiqadi va **UI tugmasiga ("+") aylanadi** |
| 4.9–6.7 | "Soatlab vaqt ketadi" | Kadr **oqqa oqib ketadi**, to'liq ekranli och rangli **to-do ilova**: sarlavha, punktlar birma-bir qo'shiladi va belgilanadi |
| 6.7–11.1 | "Natija zerikarli" | Kulrangga, keyin qoraga o'tadi. To'q rangli **chat**: vazifa kartasi va avatar, xabar pufakchalari birma-bir chiqadi (montajchining uzrlari). Ekrandagi matn nutqni takrorlamaydi, uni sahnalashtiradi |
| 11.1–15.7 | Xulosa | Spikerga qaytadi, **titr yo'q** (post shu yerda tugaydi yoki tugallanmagan; qoida qilinmadi) |

## Kadrma-kadr o'lchovlar

**Harflab yig'ilish (v1 f3–f35):**
- har bir harf alohida chiqadi, harflar orasidagi kechikish ~2 kadr;
- harf 4–5 kadrda och-ko'k (oq so'zlarda) yoki och-pushti (magenta so'zlarda) rangdan, xira va blurdan to'liq rangga o'tadi;
- keyingi so'z oldingisi tugamasdan boshlanishi mumkin;
- so'z ASR boshlanishidan −0.15…+0.05 s oldin boshlanadi (ASR aniqligi ±0.1 s).

**Plashka (v1 f56–f95):**
- magenta to'rtburchak chapdan o'ngga 8 kadrda o'sadi, keyin ustiga oq so'z harflab chiqadi;
- raqam (oq, qalin) o'z so'zida chiqadi;
- kichik magenta teg pastda o'ngda ~5 kadrda blur va scale bilan chiqadi;
- plashka balandligi ~0.034 H, eni ~0.5 W gacha.

**Romb ikonkalar (v1 f158–f179):**
- avval magenta glow dog'i paydo bo'ladi (3 kadr), keyin romb aniqlashadi (3 kadr) va biroz siljib, kattalashib joyiga tushadi;
- har bir ikonka o'z so'zida chiqadi (−0.05…0 s);
- eni ~0.18 W, bosh tepasida, romb panjarada (pastda 2 ta, tepada 1 ta).

**Negativ-flash (v1 f219–f226, f310–f315):**

| Kadr | Ko'rinish |
|---|---|
| 1 | eski kadr oq bloom bilan |
| 0–1 | eski kadr negativda yoki oddiy |
| 2–3 | yangi kadr negativda (moviy terili, qora fon) |
| 1 | yangi kadr oq bloom bilan |

- jami 5–7 kadr, keyin oddiy kadr;
- titrlar kesim bilan birga yo'qoladi;
- ovozda yuqori chastotali glitch/whoosh: +20…+30 dB.

**Magenta sarlavha (v1 f315–f361):**
- KATTA HARFLAR, cap ~0.045 H, y ~0.08 H;
- harflab chiqadi va bir vaqtda chapga suriladi, ~0.15 W/s;
- 1.5 s da qisman kadrdan chiqib ketadi.

**Drop-cap (v1 f344–f361):**
- kichik birinchi so'z chiqadi, keyin katta oq bosh harf 5 kadrda blur bilan chiqadi;
- uning o'ng tomonida 2 ta kichik qator.

**Kartalar yelpig'ichi (v2 f4–f24):**
- kartalar pastdan blur bilan ko'tariladi (f4–f13);
- keyin yelpig'ich bo'lib yoyiladi (f13–f22): markaziy karta oldinda, ikki yoni orqada va qiyshaygan.

**Bloom-glitch (v2 f72–f77):**
- 1 oq kadr (matn chiziq bo'lib cho'ziladi), 1 oddiy kadr;
- 2 negativ kadr (och fonli);
- 1 oddiy kadr, 1 bloom kadr.

**Oqqa o'tish (v2 f149–f160):**
- kadr ~8 kadrda oqqa oqadi;
- UI sarlavhasi oq ustida 3–4 kadrda paydo bo'ladi.

**Ikonka → tugma (v2 f139–f141):** dastur ikonkasi 1 kadrda oq "+" tugmaga almashadi, tugma "+" va "×" orasida tebranadi.

**Chat pufakchalari (v2 f235–f246):**
- pufakcha avval 3 kadr gorizontal blur chizig'i bo'lib chiqadi;
- keyin ~1.06 gacha kattalashib, 5–6 kadrda joyiga tushadi;
- ovozda xabar "pop"i: +25 dB yuqori chastota.

## O'lchamlar (After kadriga nisbatan)

| Element | O'lcham |
|---|---|
| Katta oq so'z | cap ~0.05 H |
| Magenta kalit so'z | cap ~0.05–0.06 H, eni 0.6–0.75 W |
| Kichik so'zlar, `[qavs]`, kulrang bog'lovchi | ~0.02 H |
| Stack bloki | y 0.2–0.62 H, chap tomonga tekislangan, qatorlar zinapoya bo'lib siljigan |
| Sarlavha (KATTA HARFLAR) | y 0.08–0.27 H |

## Rang

| Element | Rang |
|---|---|
| Aksent (magenta-binafsha) | median #C000E6, yorug' #EE39FA, glow bilan |
| Shisha kartalar | #7638CC |
| Kichik bog'lovchi so'zlar | ~50% oq |

Footage o'z rangida qoladi (kuchli grade yo'q). UI sahnalar tizim ko'rinishida: och sahna oq, to'q sahna qora va kulrang pufakchalar bilan.

## Ovoz

- Nutq ostida fon musiqasi bor: pauzalarda −29…−31 dB, jimlik emas.
- Har bir qurilmada SFX bor:
  - negativ-flash: glitch/whoosh;
  - romb ikonka: pop (+9…+15 dB);
  - chat pufakchasi: xabar pop (+25 dB);
  - oqqa o'tish: swoosh (+20 dB).

## Plaginga nima o'tdi

Plagin: `styles/skills/ui_cascade`. Unga faqat o'zgarmas qoidalar o'tdi. Bu yerdagi brendlar, so'zlar, raqamlar va vaqtlar plaginda yo'q.
