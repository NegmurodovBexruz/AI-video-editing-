# Case Reel — montaj uslubi plagini

`/styles:case_reel`: **case study** videolarni montaj qiladi. Bunday videoda spiker brend, agentlik yoki frilanser mijoz uchun qanday natijaga erishganini aytib beradi. Soha, til va uzunlik ixtiyoriy.

Montaj **qat'iy hikoya shabloni** bo'yicha quriladi:

> hook (raqamli va'da) → mijoz → muammo → strategiya → test → natija → xulosa → chaqiriq (CTA)

Uslubning asosiy elementlari:
- kichik, tinch subtitr: 2–3 so'zli chunk birdaniga chiqadi;
- bo'lim boshlanishida sarlavha subtitri;
- natija raqamlari slot-mashina kabi aylanuvchi hisoblagich va progress bar bilan chiqadi;
- hamkor va platformalar nomi aytilganda badge chiqadi;
- mijoz ishlari 2 kadrlik strobe-montajda tez o'tadi;
- bo'limlar orasida film-burn light leak;
- oxirida agentlik belgisi.

**Boshqa uslublardan farqi:**
- brand_stage va pod_glow'da asosiy narsa **ko'rinish**;
- Case Reel'da asosiy narsa **hikoya tuzilishi va raqamlar bilan isbot**.

**Muhim qoida:** ekranga chiqadigan har bir raqam faqat foydalanuvchi bergan natija ma'lumotlaridan olinadi. Mijoz media'si va hamkor logolari faqat ruxsat bilan ishlatiladi. Sabab: reklama ommaviy da'vo hisoblanadi.

Plaginda faqat uslubning **o'zgarmas qoidalari** bor.
- U qaysi dasturda qurilishiga bog'liq emas.
- Soha va uzunlikka ham bog'liq emas: bo'limlar ulush sifatida, zichlik "har necha soniyada" deb yozilgan, o'lchamlar kadrga nisbatan berilgan.
- Plaginda API kalitlari yoki MCP sozlamalari yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin `/styles:case_reel` yozing va raw videoni bering. Imkoni boricha quyidagilarni ham qo'shing:
- **natija ma'lumotlari:** raqamlar, davr, nima o'lchangani;
- mijoz mahsulot rasmlari va reklamalari (ruxsat bilan);
- agentlik logosi va ranglari;
- hamkor logolarini ko'rsatishga ruxsat.

Agent avval reja, raqamlar jadvali va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Tarkibi

- `skills/case_reel/SKILL.md`: uslubning DNK'si va 10 bosqichli ish tartibi (raqamlarni tekshirish va 2 ta tasdiq bosqichi bilan).
- `references/structure.md`: hikoya shabloni: 8 bo'lim, ularning vazifasi, ulushi, nutqdagi belgilari, ekrandagi belgilari.
- `references/captions.md`: kichik chunk subtitr, sarlavha subtitri, hook yozuvlari, vaqt, kontrast (oq fon ustida o'qilishi).
- `references/beat-map.md`: "lahza → vosita" jadvali va har qanday uzunlik uchun zichlik.
- `references/devices.md`: slot-hisoblagich, progress bar, hamkor badge, strobe-montaj, telefon UI ramka, B-roll, film-burn, agentlik belgisi.
- `references/motion.md`: o'tishlar va kadr hisoblari.
- `references/look.md`: bo'limlar bo'yicha grade, palitra, bepul shriftlar.
- `references/sound.md`: musiqa foni, hisoblagich tovushlari, montaj pulsi, loudness, litsenziyalar.
- `references/qa.md`: tuzoqlar, raqamlar va ruxsatlar, generatsiya qoidalari, tekshiruv ro'yxati, zaxira yo'llar.

**Ma'lum cheklovlar:**
- Uslub bitta namunadan yozilgan. Yana namunalar qo'shilsa, qoidalar aniqroq bo'ladi.
- Asl shriftlar aniqlanmagan, o'rniga bepul (OFL) muqobillar berilgan.
- Namunada o'tishlardagi SFX'larni nutqdan ajratib bo'lmadi, shuning uchun ovoz qoidalari umumiy darajada yozilgan.
