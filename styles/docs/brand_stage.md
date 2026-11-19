# Brand Stage — montaj uslubi plagini

`/styles:brand_stage`: bitta spiker brend, studiya, agentlik yoki mahsulot nomidan gapiradigan videoni (mavzu, til va uzunlik ixtiyoriy) "Brand Stage" uslubida montaj qiladi.

Spiker kadrida faqat **minimal oq subtitr** bo'ladi:
- mazmunli so'zlar katta, yordamchi so'zlar kichik;
- har bir so'z ovozi eshitilgan zahoti o'z joyida kulrangdan oqqa o'tib chiqadi.

Grafikaning hammasi **brend sahnasida**, ya'ni brend rangidagi to'liq ekran maydonda bo'ladi:
- tilga olingan narsalar shoxlangan diagramma bo'ylab kartalar bo'lib chiqadi;
- asosiy g'oya nurli halqali konsept badge bo'ladi;
- o'z ishlari telefon shaklidagi portfolio kartalarda ko'rsatiladi.

Yana: to'liq ekranli showcase B-roll, boshida va oxirida brend belgisi sting'i, iris → nuqta, glitch-smear va zarrachaga sochilish o'tishlari.

**Boshqa uslublardan farqi:**
- talk_ahead faktlarni isbotlaydi: hisoblagich, xarita, spiker ortidagi so'zlar;
- pod_glow podkastda ishlaydi: 2 qavatli to'q sariq glow subtitr;
- Brand Stage'da spiker kadri **jim va toza**, butun "shou" brend sahnasida bo'ladi.

Plaginda faqat uslubning **o'zgarmas qoidalari** bor: qoidalar, o'lchamlar, vaqtlar va ish tartibi.
- U qaysi dasturda qurilishiga bog'liq emas.
- Mavzu, brend va uzunlikka ham bog'liq emas: zichlik "har necha soniyada bitta" deb yozilgan, o'lchamlar kadrga nisbatan berilgan.
- Plaginda API kalitlari yoki MCP sozlamalari yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin `/styles:brand_stage` yozing va raw videoni bering. Imkoni bo'lsa quyidagilarni ham qo'shing:
- brend belgisi (logo) va ranglari;
- portfolio rasmlari yoki videolari;
- gapda tilga olingan mahsulotlar logolarini ko'rsatishga ruxsat.

Agent avval reja va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Tarkibi

- `skills/brand_stage/SKILL.md`: uslubning DNK'si va 9 bosqichli ish tartibi (2 ta tasdiq bosqichi bilan).
- `references/captions.md`: editorial oq subtitr: chunk'lar, o'lcham ierarxiyasi, joylashuv, so'z vaqti (ovoz boshlanishiga) va kulrangdan oqqa chiqish, UI-teg varianti.
- `references/beat-map.md`: "gap nima qiladi → qaysi vosita" jadvali va har qanday uzunlik uchun zichlik.
- `references/devices.md`: brend sahnasi, diagramma, kartalar, badge, portfolio, B-roll, zarracha, sting'larning tuzilishi.
- `references/motion.md`: o'tishlar va kadr hisoblari.
- `references/look.md`: grade, sahna rangi (brend bo'yicha), palitra, bepul shriftlar.
- `references/sound.md`: musiqa foni, sahna zarbalari, sting ovozi, loudness, litsenziyalar.
- `references/qa.md`: tuzoqlar, logo va ruxsatlar, generatsiya qoidalari, tekshiruv ro'yxati, zaxira yo'llar.

**Ma'lum cheklovlar:**
- Uslub bitta namunadan yozilgan. Yana namunalar qo'shilsa, qoidalar aniqroq bo'ladi.
- Asl shriftlar aniqlanmagan, o'rniga bepul (OFL) muqobillar berilgan.
- Ovoz tahlilida o'tishlardagi whoosh'larni nutqdan ajratib bo'lmadi, shuning uchun ular "ixtiyoriy, past" deb yozilgan.
