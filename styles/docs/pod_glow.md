# Pod Glow — montaj uslubi plagini

`/styles:pod_glow`: podkast, intervyu yoki suhbat klipini (bir yoki bir necha spiker mikrofon oldida, mavzu va til ixtiyoriy) "Pod Glow" uslubida montaj qiladi. Spikerlar gapiradi, ekran esa ular nimani **nazarda tutayotganini** ta'kidlaydi:
- har bir gap nurli kalit ibora bilan tugaydi: kichik oq kirish so'zlari ustida, katta to'q sariq (aksent) ibora ostida, ko'krak balandligida;
- har bir g'oyaga bitta toza, interfeys uslubidagi karta chiqadi (orbita, network, egilgan 3D kartalar, shisha panel, ichi bo'sh "???");
- spiker almashganda oq flash bo'ladi;
- iliq grade, tepa va pastda qora bandlar;
- musiqa foni va o'tishlarda zarba.

**talk_ahead'dan farqi:** talk_ahead faktlarni (raqam, joy, taqqoslash) isbotlaydi. Pod Glow esa fikr, his va tushunchalarni ko'rsatadi. Uning asosiy vositasi subtitr, hisoblagich yoki xarita emas.

Plaginda faqat **uslub** bor: qoidalar, o'lchamlar, vaqtlar va ish tartibi. U qaysi dasturda qurilishiga bog'liq emas. Ish vositalari agentning o'zida bo'lishi kerak: ffmpeg, speech-to-text, motion-graphics vositasi yoki kompozitor, rasm generatori, musiqa manbai. Plaginda API kalitlari yoki MCP sozlamalari yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```
Keyin `/styles:pod_glow` yozing va raw videoni bering. Xohlasangiz brend rangi, shriftlar, spikerlar ismi yoki logoni ham qo'shing. Agent avval reja va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Tarkibi

- `skills/pod_glow/SKILL.md`: uslubning DNK'si va 9 bosqichli ish tartibi (2 ta tasdiq bosqichi bilan).
- `references/captions.md`: 2 qavatli subtitr tizimi: kalit iborani tanlash, o'lchamlar, **so'z vaqti (ovoz boshlanishiga)** va **so'zning kirish harakati**, emoji va ikonkalar.
- `references/beat-map.md`: "qanday g'oya → qaysi vosita" jadvali va zichlik qoidalari.
- `references/devices.md`: har bir kartaning aniq tuzilishi, kadr hisobidagi vaqtlari va o'lchamlari.
- `references/look.md`: grade, qora bandlar, palitra, bepul shrift muqobillari, brend rangini almashtirish.
- `references/motion.md`: pop egri chizig'i, o'tishlar, flash, re-frame, temp tekshiruvi.
- `references/sound.md`: musiqa foni, zarbalar, UI pop'lar, loudness, litsenziyalar.
- `references/qa.md`: tuzoqlar, generatsiya qoidalari, har renderdan keyingi tekshiruv (shu jumladan har bir so'zning vaqtini ovozga solishtirish), zaxira yo'llar.

Plaginda faqat uslubning **o'zgarmas qoidalari** bor. Bitta videoning vaqtlari, jadvali yoki test natijalari bu yerda yo'q.
- Qoidalar mavzuga bog'liq emas: ular "kalit ibora", "tushuncha", "emotsiya", "odamlar guruhi", "savol", "nomlangan atama" kabi umumiy toifalar haqida.
- Uzunlikka ham bog'liq emas: zichlik "har necha soniyada bitta" deb yozilgan, shuning uchun 20 soniyalik klipga ham, 3 daqiqalik intervyuga ham mos keladi.
- O'lchamlar 1080×1920 uchun berilgan, boshqa kadrlar uchun nisbat bilan o'tkaziladi.

**Ma'lum cheklovlar:**
- Uslub bitta namunadan yozilgan. Yana namunalar qo'shilsa, qoidalar aniqroq bo'ladi.
- Asl shriftlar aniqlanmagan, o'rniga bepul (OFL) muqobillar berilgan.

**v0.2.0 (2026-11-04):** subtitr qoidalari kadrma-kadr (1/30 s) o'lchov asosida qayta yozildi:
- so'z o'zi eshitilganda chiqadi, hech qachon oldin emas;
- so'z 2–3 kadrda yuqoridan tushib joylashadi, blok o'zi harakatlanmaydi;
- har bir so'zda alohida gradient, ingichka kontur va soya;
- kichik qator ham keng kursiv shriftda.

Bir videoga xos ma'lumotlar plagindan olib tashlandi.
