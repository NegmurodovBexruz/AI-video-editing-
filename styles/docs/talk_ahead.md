# Talk Ahead — montaj uslubi plagini

`/styles:talk_ahead`: gapiruvchi spiker videosini (talking-head) "Talk Ahead" uslubida montaj qiladi. Spiker gapiradi, ekran esa uning har bir faktini isbotlaydi: hook so'zi spiker orqasida turadi, raqamlar hisoblagich yoki odometr bo'ladi, kadrda yo'q obyektlar AI insert bo'lib chiqadi, masofalar real xaritada ko'rsatiladi, o'tishlar brend motivi bilan qilinadi, subtitr butun nutq bo'yicha so'zma-so'z chiqadi, ovoz brend materialidan olinadi (whoosh ishlatilmaydi).

Plaginda faqat **uslub** bor: qoidalar, vaqtlar, joylashuv, ish tartibi va namuna. Vositalar agentning o'zida bo'lishi kerak: ffmpeg, maska modeli, Higgsfield MCP, ovoz va musiqa generatori, speech-to-text. Plaginda API kalitlari yoki MCP sozlamalari yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```
Keyin `/styles:talk_ahead` yozing va raw videoni bering. Ixtiyoriy ravishda brandbook, logo yoki referens videoni ham qo'shishingiz mumkin. Agent avval reja va narxni ko'rsatadi, siz tasdiqlaganingizdan keyingina kredit sarflaydi.

## Tarkibi

- `skills/talk_ahead/SKILL.md`: uslubning DNK'si va 9 bosqichli ish tartibi (2 ta tasdiq bosqichi bilan).
- `references/beat-map.md`: nutqdagi narsa → ekrandagi vizual jadvali va zichlik qoidalari.
- `references/motion.md`: har bir effektning aniq vaqtlari, easing'i va o'lchamlari.
- `references/typography.md`: shriftlarning rollari, xavfsiz zonalar, subtitr qoidalari.
- `references/brand-motif.md`: brandbook'dan rang, shrift va logo olish; logodan bitta motiv chiqarish.
- `references/sound.md`: ovoz qoidalari, musiqa brifi, litsenziyalar.
- `references/qa.md`: tuzoqlar, generatsiya qoidalari, har bir renderdan keyingi tekshiruv ro'yxati.
- `references/example-spc.md` va `examples/`: SPC namunasi, har bir lahza qaysi vizualga aylangani va kadrlar bilan.

Uslub mavzuga bog'liq emas: qoidalar biror soha haqida emas, "raqam", "obyekt", "solishtirish", "joy", "savol" kabi umumiy toifalar haqida yozilgan.
