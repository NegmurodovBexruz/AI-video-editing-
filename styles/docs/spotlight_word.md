# Spotlight Word — montaj uslubi plagini

`/styles:spotlight_word`: kamera oldida gapiradigan inson videosini montaj qiladi. Bu odatda o'zini, ishini, yo'lini yoki kompaniyasini tanishtiradigan video bo'ladi. Mavzu, til va uzunlik ixtiyoriy.

Uslubning asosiy elementlari:
- **Subtitr:** oq kichik so'zlar bittadan chiqadi.
- **Spotlight so'zlar:** muhim so'zlar katta, tekis sariq va yumshoq glow bilan chiqadi. Bular ism, lavozim, brend, joy va hal qiluvchi fe'l. Ulardan oldingi kichik so'zlar ustida turadi.
- **Qo'lyozma aksentlar:** ism, brend yoki joyning ikkinchi so'zi oq qo'lyozma bo'lib yozilib chiqadi.
- **O'z ishlari:** spikerning ishlari to'liq kadrda ko'rsatiladi, plitkali o'tishlar bilan.
- **Joylar:** shu joy fotosurati ustiga nomi katta ikki rangli harflar bilan yoziladi.
- **Yo'l va o'sish:** "X dan Y gacha" kabi gaplar uchun metafora kadri. Spiker tepadagi oynaga kichrayadi, pastda g'oyaning illyustratsiyasi chiqadi.
- **Type echo:** kalit so'z ustun bo'lib takrorlanadi.

Boshqa uslublardan farqi: subtitr chunk yoki 2 qavatli emas, **bitta so'zdan** iborat va unga **spotlight** so'zlar qo'shiladi. Grafika esa ma'lumot yoki UI kartalari emas, **metafora va joylar**.

Plaginda faqat uslubning **o'zgarmas qoidalari** bor.
- U qaysi dasturda qurilishiga bog'liq emas.
- Mavzu va uzunlikka ham bog'liq emas: zichlik "har necha soniyada" deb yozilgan, o'lchamlar kadrga nisbatan berilgan.
- **"Before / After" post foni** (ikki karta va dog'lar) plaginga kirmaydi. Uslub faqat "After" montajidan olingan.
- Plaginda API kalitlari yoki MCP sozlamalari yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin `/styles:spotlight_word` yozing va raw videoni bering. Imkoni bo'lsa quyidagilarni ham qo'shing:
- o'z ishlaringiz (rasm, render, mahsulot);
- tilga olingan joylarning fotosuratlari;
- brend ranglari va shriftlari.

Agent avval reja va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Tarkibi

- `skills/spotlight_word/SKILL.md`: uslubning DNK'si va 9 bosqichli ish tartibi (2 ta tasdiq bosqichi bilan).
- `references/captions.md`: bitta so'zli subtitr, spotlight tanlash, o'lchamlar, stack swap, qo'lyozma aksentlar, vaqt (ovoz boshlanishiga).
- `references/beat-map.md`: "lahza → vosita" jadvali va har qanday uzunlik uchun zichlik.
- `references/devices.md`: metafora kadri, joy illyustratsiyasi, foto ustidagi joy yozuvi, plitkali o'tish, type echo, brend uchun naqsh, ish B-roll'i.
- `references/motion.md`: kirish va chiqish harakatlari, kadr hisoblari.
- `references/look.md`: palitra, bepul shriftlar, grade, brend rangini almashtirish.
- `references/sound.md`: ixtiyoriy musiqa foni, zarbalar, loudness, litsenziyalar.
- `references/qa.md`: tuzoqlar, media ruxsatlari, generatsiya qoidalari, tekshiruv ro'yxati, zaxira yo'llar.

**Ma'lum cheklovlar:**
- Uslub bitta **17 soniyalik** namunadan yozilgan, dalil kam. Shu uslubdagi yana namunalar qo'shilsa, qoidalar mustahkamlanadi.
- Asl shriftlar aniqlanmagan, o'rniga bepul (OFL) muqobillar berilgan.
- Namunada doimiy musiqa foni aniqlanmadi, shuning uchun musiqa ixtiyoriy deb yozilgan.
