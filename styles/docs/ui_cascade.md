# UI Cascade: montaj uslubi

`/styles:ui_cascade`: bitta spiker gapiradigan videoni montaj qiladi. Mavzu, til va uzunlik ixtiyoriy.

**Asosiy g'oya:** so'zlar spiker atrofida harflab "oqib" yig'iladi. Har bir iborada bitta so'z binafsha-magenta rangda yonadi. Nutq biror narsani, kontentni yoki jarayonni nomlasa, u interfeys bo'lib chiqadi: ikonka, karta yoki ilova ekrani. Har bir kamera almashinuvi negativ-flash bilan kesiladi.

## Uslubning asosiy elementlari

- **Harflab yig'ilish.** Har bir harf alohida, xira va sovuq tusda kiradi, bir necha kadrda to'liq rangga o'tadi. Ibora o'chmaydi, o'sib boradi.
- **Stack titr.** Ibora zinapoyasimon blok bo'ladi:
  - katta oq so'zlar;
  - xira bog'lovchi so'zlar;
  - `[qavs ichidagi]` kichik izohlar;
  - **bitta** magenta kalit so'z, glow bilan.
- **Raqam plashkada.** Aksent rangli plashka chapdan o'sadi, ustiga raqam yoziladi, birlik (so'm, %) pastda kichik teg bo'ladi.
- **Sarlavha va drop-cap.** Katta da'vo uchun bosh tepasida asta yonga suriladigan KATTA HARFLI magenta sarlavha ishlatiladi. Xulosa uchun katta oq bosh harf va uning yonida kichik qatorlar.
- **Narsalar ikonka bo'ladi.** Sanalgan narsa, brend yoki xizmat bosh tepasida yaltiroq 3D romb ikonka bo'lib chiqadi, har biri o'z so'zida.
- **Kontent kartaga aylanadi.** Video yoki postlar shisha kartalar yelpig'ichi bo'lib chiqadi, ustida hisoblagich bo'ladi.
- **Jarayon ilova sahnasiga aylanadi.** To'liq ekranga chiqadi, ichiga oq yoki qora fon orqali o'tiladi:
  - vazifalar ro'yxati — to-do ilova;
  - uzrlar yoki xabarlar — chat pufakchalari;
  - harakat — tugma.
- **Har bir kesimda negativ-flash.** Oq bloom kadr, 2–3 negativ kadr, yana oq kadr, ovozda glitch.

## Boshqa plaginlardan farqi

- `pod_glow` da titr qat'iy ikki qavatli, har g'oyaga bitta karta chiqadi. Bu yerda titr erkin stack bo'lib harflab yig'iladi, g'oyalar esa to'liq ekranli ilova sahnasiga aylanadi.
- `spotlight_word` bittadan so'z ko'rsatadi. Bu yerda butun ibora turadi va o'sib boradi.
- `in_scene_type` spikerdan chiqmaydi. Bu yerda UI sahnasiga chiqiladi.

**Plaginda faqat o'zgarmas qoidalar bor:**
- qaysi dasturda qurilishiga bog'liq emas;
- o'lchamlar kadrga nisbatan, zichlik "har necha soniyada" bilan berilgan;
- bitta videoning brendi, so'zi yoki raqami yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin `/styles:ui_cascade` yozing va raw videoni bering. Ixtiyoriy ravishda qo'shishingiz mumkin:
- brend rangi;
- tilga olinadigan narsalar logolari (ruxsat bilan);
- kartalar uchun o'z kontentingiz.

Agent avval reja va narxni ko'rsatadi.

## Tarkibi

| Fayl | Mazmuni |
|---|---|
| `skills/ui_cascade/SKILL.md` | uslub DNK'si va 9 bosqichli ish tartibi |
| `references/captions.md` | harflab yig'ilish, stack, so'z rollari, plashka, sarlavha, drop-cap, vaqt |
| `references/beat-map.md` | nutq vazifasi → qurilma, zichlik |
| `references/devices.md` | romb ikonkalar, karta yelpig'ichi, ikonka → tugma, ilova sahnalari, negativ-flash, bloom-glitch |
| `references/motion.md` | kadr sonlari va easing |
| `references/look.md` | palitra, shriftlar, glow, shisha, UI ko'rinishi |
| `references/sound.md` | fon, har bir qurilmaning SFX'i, loudness |
| `references/qa.md` | tuzoqlar, ruxsatlar, tekshiruv ro'yxati, zaxira yo'llar |

## Qayerdan olingan

- **Manba:** ikkita Before/After portfolio posti. Faqat ularning After qismi tahlil qilingan.
- **Tahlil:** `refs/ref_ba_20261109/analysis.md`. Kadrma-kadr o'lchovlar (1/30 s), ASR va ovoz tahlili shu yerda.

## Ma'lum cheklovlar

- **Faqat 2 ta namuna,** ikkalasi bitta montajchidan. Yana namunalar qo'shilsa, qoidalar mustahkamlanadi.
- **Shriftlar taxminiy.** Asl shriftlar aniqlanmagan, o'rniga bepul (OFL) muqobillar berilgan.
- **Ovoz.** Namunalarda SFX nutq va fon bilan aralash edi. SFX turlari baland chastotali cho'qqilardan aniqlangan, aniq tovushlar tasdiqlanmagan.
- **Real videoda hali sinalmagan.** Dvijokda renderer'i yo'q.
