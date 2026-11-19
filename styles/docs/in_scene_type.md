# In-Scene Type — montaj uslubi plagini

`/styles:in_scene_type`: bitta spiker kamera oldida gapiradigan videoni montaj qiladi. Mavzu, til va uzunlik ixtiyoriy.

Asosiy g'oya: montaj spikerdan **hech qachon uzoqlashmaydi**. B-roll ham, to'liq ekranli karta ham yo'q. Butun energiya spikerning o'z kadridagi matn va kamera harakatidan keladi.

Uslubning asosiy elementlari:
- **Har bir gap alohida kompozitsiya.** Gapning bitta kalit so'zi katta, qolganlari kichik. Har so'z o'z tovushida chiqadi, gap tugaganda kompozitsiya yo'qoladi.
- **Chuqurlikdagi matn.** Ulkan condensed bosh harfli so'z **boshning orqasida** turadi (person matte bilan) yoki **oldinda**, ko'krak ustida.
- **Kichik so'zlar boshga bog'langan.** Bosh yonidagi kichik qatorlar har kadrda bosh bilan birga suriladi: kechikishsiz, prujinasiz.
- **Shriftlar tizimi.** Kalit so'zlar uchun condensed caps, kichik so'zlar uchun sans, raqamlar uchun ingichka serif italic, his-tuyg'u so'zi uchun script. Kalit so'z ostida kichik aksent rangli qator turadi.
- **So'z sahnadan chiqadi.** Spiker barmoq bilan ko'rsatgan raqam qo'lning o'zida paydo bo'ladi. Script so'z kiyim yoki mebel ustiga yozib chiqiladi.
- **Kamera nafas oladi.** Punch → hold → release; katta so'zga joy ochadigan zoom-out reveal; set-up oxirida tezlashib boradigan push. Oxirgi set-up esa tinch.
- **Fizik o'tishlar.** Set-up almashganda cellophane (plastik plyonka) wipe yoki glow-siluet flash ishlatiladi.

Boshqa plaginlardan farqi:
- `brand_stage` va `case_reel` boshqa sahna yoki kartalarga o'tadi, bu uslub esa spikerdan chiqmaydi.
- `spotlight_word` bitta so'zli subtitr ishlatadi, bunda esa matn kadr chuqurligida joylashgan va boshni kuzatadi.

Plaginda faqat uslubning **o'zgarmas qoidalari** bor:
- qaysi dasturda qurilishiga bog'liq emas;
- mavzu va uzunlikka bog'liq emas: zichlik "har necha soniyada", o'lchamlar kadr yoki yuz kengligiga nisbatan berilgan;
- API kalitlari yoki MCP sozlamalari yo'q.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin `/styles:in_scene_type` yozing va raw videoni bering.
- Iloji bo'lsa yuqori sifatli manba bering (4K yoki 1440p), shunda punch-in'lar xira chiqmaydi.
- Tilga olinadigan tashkilotlarning logotiplarini faqat ruxsat bo'lsa bering.

Agent avval reja va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Tarkibi

| Fayl | Mazmuni |
|---|---|
| `skills/in_scene_type/SKILL.md` | uslub DNK'si va 9 bosqichli ish tartibi (2 ta tasdiq bosqichi bilan) |
| `references/type.md` | qatlamlar, kalit so'z tanlash, o'lcham va joylashuv, boshga bog'lash, vaqt (ovoz boshlanishiga) |
| `references/beat-map.md` | "nutq → kompozitsiya, kamera, vosita" jadvali, har qanday uzunlik uchun zichlik |
| `references/camera.md` | punch, hold, release, reveal, push: o'lchamlar, kadr soni, easing |
| `references/devices.md` | bosh orqasidagi so'z, boshga bog'langan blok, qo'ldan chiqadigan raqam, write-on, serif raqamlar, ko'krakdagi logo, cellophane va glow o'tishlari |
| `references/motion.md` | har bir qatlamning kirish va chiqish animatsiyasi |
| `references/look.md` | palitra, bepul shriftlar, grade, brendga moslash |
| `references/sound.md` | fon musiqasi, o'tish tovushlari, loudness, litsenziyalar |
| `references/qa.md` | tuzoqlar, ruxsatlar, generatsiya, tekshiruv ro'yxati, zaxira yo'llar |

## Ma'lum cheklovlar

- Uslub bitta **40 soniyalik** namunadan olingan. Yana namunalar qo'shilsa, qoidalar mustahkamlanadi.
- Namunada **nutq yo'q edi** (faqat past fon). Shuning uchun so'zning ovozga tushish qoidasi namunadan o'lchanmagan, umumiy qoidamiz olingan: so'z tovush boshlanishida chiqadi, hech qachon erta emas.
- Ovoz qatlami (`sound.md`) ham namunadan emas, uslubga mos umumiy tavsiya.
- Aksent rangini kompressiya tufayli aniq o'lchab bo'lmadi, standart amber rang taxminiy.
- Asl shriftlar aniqlanmagan, o'rniga bepul (OFL) muqobillar berilgan.
- Cellophane o'tishi uchun stock yoki generatsiya qilingan overlay kerak.
