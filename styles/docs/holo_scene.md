# Holo Scene: montaj uslubi

`/styles:holo_scene`: spiker haqiqiy joyda gapiradigan videoni montaj qiladi. Bu brend, mahsulot, xizmat haqidagi yoki fakt tushuntiradigan video bo'lishi mumkin. Mavzu, til va uzunlik ixtiyoriy.

Asosiy g'oya: spiker aytgan har bir da'vo **o'sha joyning o'zida isbotlanadi**. U nomlagan narsa cyan gologramma bo'lib haqiqiy yuzalarda paydo bo'ladi:
- kaftlarda;
- takrorlanuvchi narsalar devorida (javon, shtabel);
- polda yoki stolda;
- bosh tepasida.

Uslubning asosiy elementlari:
- **Stack titrlar.** Har bir ibora uch qismdan iborat: tepada kichik so'z, o'rtada bitta ulkan kalit so'z, ostida kichik qatorlar.
  - Uzun kalit so'z **bosh orqasida** turadi, bosh bir nechta harfni yopadi.
  - Raqamli va qisqa kalit so'zlar boshdan yuqorida, to'liq o'qiladi.
  - Kichik qatorlar iyakdan pastda turadi. Har bir so'z o'z tovushida xira chiqadi va oqaradi.
- **Gologramma:** qirra chiziqlari, scanline'li shaffof to'ldirish va glow. U scan chizig'i bilan ochiladi.
- **Miqdor ko'z oldida sodir bo'ladi:**
  - qatorlar pastdan yuqoriga yonadi;
  - narsalar ustidan to'lqin yuradi va hisoblagich sanaydi;
  - gologramma uchqunlarga aylanib, haqiqiy narsalarga uchib kiradi va ular ichidan yonadi.
- **Bitta sho'ng'ish.** Filmda bir marta kamera mavzuning ichiga sho'ng'iydi va CGI interyer bo'ylab uchadi. Devorlarda da'voning belgilari o'tadi, oxiri oq bilan tugaydi.
- **Mahsulot ekrani zarrachalardan yig'iladi.** Unda haqiqiy sayt yoki ilova ko'rsatiladi, kursor uni ishlatadi.
- **Jonli yakuniy karta.** Brend belgisi va URL. Karta oxirgi kadrgacha harakatda bo'ladi.

**Boshqa plaginlardan farqi:**
- `in_scene_type` spikerda qoladi va faqat matn ishlatadi.
- `brand_stage` tekis brend sahnasiga o'tadi.
- `case_reel` mijozning ishlaridan montaj qiladi.
- Holo Scene esa **haqiqiy joyni saqlab, unga yorug'likdan yasalgan narsalarni qo'shadi**.

**Plaginda faqat o'zgarmas qoidalar bor:**
- qaysi dasturda qurilishiga bog'liq emas;
- o'lchamlar W, H va yuz kengligiga nisbatan berilgan;
- zichlik "har necha soniyada" bilan berilgan.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin `/styles:holo_scene` yozing va raw videoni bering. Imkoni bo'lsa, quyidagilarni ham qo'shing:
- brend belgisi va ranglari;
- mahsulot yoki sayt manzili;
- aniq ko'rinishi kerak bo'lgan obyektlarning erkin litsenziyali fotolari.

Agent avval reja va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Tarkibi

| Fayl | Mazmuni |
|---|---|
| `skills/holo_scene/SKILL.md` | uslub DNK'si va 9 bosqichli ish tartibi (2 ta tasdiq bosqichi bilan) |
| `references/captions.md` | stack, kalit so'z tanlash va joylashtirish (bosh orqasida yoki ustida), o'lchamlar, yorug' fon ustida o'qilishi |
| `references/beat-map.md` | "da'vo → qurilma → yuza" jadvali, zichlik, hikoya shakllari, reja jadvali |
| `references/devices.md` | gologramma qurish, qatorlarni yoqish, to'lqin va hisoblagich, kaftdagi obyekt, uchqunlar, kesim chizmasi, poldan o'sish, sho'ng'ish, cutaway yozuvi, ekran, yakuniy karta |
| `references/motion.md` | har bir element va o'tishning kadr sonlari, kamera |
| `references/look.md` | palitra, shriftlar, grade, brendga moslash |
| `references/sound.md` | musiqani zarbaga moslash, har bir qurilmaning SFX'i, loudness |
| `references/qa.md` | tuzoqlar, litsenziya va ruxsatlar, generatsiya qoidalari, tekshiruv ro'yxati, zaxira yo'llar |

## Qayerdan olingan

- **Referens:** `refs/ref_C053443` (41 s agentlik case videosi). Tahlili `analysis.md` da.
- **Birinchi real sinov:** Sklet × SPC montaji (`projects/sklet_c053`, 73.62 kredit). Undan quyidagi qoidalar olingan:
  - raqamlar boshdan yuqorida turadi;
  - oq fon ustida matn navy rangga o'tadi;
  - yakuniy karta jonli bo'ladi;
  - musiqa zarbasi so'zga moslanadi;
  - sayt preloader'dan keyin suratga olinadi.

## Ma'lum cheklovlar

- **Faqat bitta referens.** Uslub bitta videodan olingan, boshqa namunalar qo'shilsa, qoidalar mustahkamlanadi.
- **Kamera harakati.** Ikkala video ham statik yoki sekin kamerada olingan. Kamera kuchli harakatlansa, yuzani kuzatish (tracking) kerak bo'ladi (`qa.md`).
- **Dvijok renderer'i yo'q.** Agent kompozitorni o'zi yozadi. Sklet uchun yozilgan kompozitor (`projects/sklet_c053/scripts/compose.py`) namuna sifatida turibdi.
