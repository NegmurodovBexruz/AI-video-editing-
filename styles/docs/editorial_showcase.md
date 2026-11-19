# Editorial Showcase — montaj uslubi

`/styles:editorial_showcase` — bitta spiker xizmatni, mahsulotni yoki ish jarayonini tushuntirib, misollar va tayyor ishlarni ko'rsatadigan videolar uchun. Versiya: **0.1.0**. Holat: **qoidalar tayyor, yangi raw videoda hali sinalmagan**.

Uslub ikki vazifani birlashtiradi:
- tushuntirish: serif matn, qisqa kursiv/qo'lyozma aksent, xabar, ta'rif kartasi va hujjat sahnasi;
- namoyish: spiker ostidagi demo, telefon/ekran ichidagi ish, uch gorizontal qator va perspektivali panel o'tishi.

Qaysi qurilma ishlatilishini nutqning vazifasi belgilaydi. Har videoga barcha effektlar qo'yilmaydi. Yagona ko'rinishni ikkita shrift oilasi, bitta aksent rang, neytral fonlar va cheklangan o'tishlar saqlaydi. Sahnalar ichida ko'rsatilgan haqiqiy ishlar o'z rangida qoladi.

## Qayerga mos

- Xizmat yoki tushunchani misollar bilan tushuntirish.
- Portfolio va mahsulot namoyishi.
- Vazifa, yechim va tayyor ishni ko'rsatadigan case.

`case_reel` hikoya va o'lchangan natijalarga, `brand_stage` brend-rang sahnasiga, bu uslub esa **tushuntirish va namoyishni navbatlashga** tayanadi. Raqamli natija yoki gologramma majburiy emas.

## Kerakli material

Raw video asosiy manba. Sayt yozuvi, portfolio, mahsulot kadrlari yoki hujjat sahifalari bo'lsa, namoyish aniqroq chiqadi. Media yetishmasa, agent konsept kartasi yoki spiker kadrini tanlaydi; soxta portfolio yasamaydi. Brandbook va tasdiqlangan transkript ixtiyoriy.

Asosiy effektlar lokal 2D/2.5D kompoziting bilan quriladi. Pulli generatsiya majburiy emas; zarur bo'lsa narx va mavjud tasdiq tekshiriladi.

## Ishlatish va holat

Mavjud `styles` plagini bilan `/styles:editorial_showcase` chaqiriladi yoki dashboardda **Editorial Showcase** tanlanadi. Dashboardning avtomatik tanlovi ham uni ko'ra oladi.

Bu **skill**, tayyor renderer emas. Engine'da `editorial_showcase` renderer'i hozircha yo'q. Dashboard agenti umumiy tahlildan foydalanib, kerakli kompozitorni ish papkasida yozadi. Shu sabab hozircha tezlik va natija barqarorligi amaliy sinov bilan tasdiqlanmagan.

## Tarkib

- `SKILL.md`: uslub DNK'si, kiruvchi material va ish tartibi.
- `beat-map.md`: nutq vazifasi → ekran turi, zichlik va reja.
- `look.md`, `captions.md`: yagona tipografika, palitra, o'qilish va sinxron.
- `devices.md`, `motion.md`: tanlanadigan qurilmalar, o'tishlar va harakat qoidalari.
- `sound.md`, `qa.md`: ovoz, tekshiruvlar va zaxira variantlari.

Asl manbalardagi shriftlar aniq identifikatsiya qilinmagan; tavsiya qilingan oilalarda har bir tilning gliflari tekshiriladi. Musiqa/SFX qoidalari umumiy loyiha talablari va ushbu vizual til uchun tuzilgan tavsiyalar; ajratilgan original treklar nusxasi emas.
