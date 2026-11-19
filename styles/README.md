# Styles: montaj uslublari plagini

Bitta plagin ichida 9 ta montaj uslubi bor. Har bir uslub alohida skill bo'lib ishlaydi. Qoidalar o'zgarmas: qaysi dasturda qurilishiga, mavzuga va uzunlikka bog'liq emas.

## Ishlatish

```
claude --plugin-dir "D:\projects\higgsfield test01\styles"
```

Keyin kerakli uslubni chaqiring, masalan `/styles:pod_glow`, va raw videoni bering. Agent avval reja va narxni ko'rsatadi. Kredit faqat siz tasdiqlaganingizdan keyin sarflanadi.

## Uslublar

| Skill | Versiya | Qanaqa video uchun | Asosiy belgisi | Batafsil |
|---|---|---|---|---|
| `talk_ahead` | 0.2.0 | Talking-head explainer | Har bir fakt vizualga aylanadi: spiker orqasida matn, hisoblagich, AI insert, real xarita, brend motivli o'tish | [docs/talk_ahead.md](docs/talk_ahead.md) |
| `pod_glow` | 0.2.1 | Podkast, intervyu, suhbat | Ikki qatorli key-phrase titr, bitta yonib turadigan aksent, spiker almashganda oq flash, UI uslubidagi kartalar | [docs/pod_glow.md](docs/pod_glow.md) |
| `brand_stage` | 0.1.0 | Bitta spiker brend, studiya yoki agentlik nomidan gapiradi | Minimal oq titr, to'liq ekranli brend-rang sahnasi, showcase B-roll, brend-mark sting | [docs/brand_stage.md](docs/brand_stage.md) |
| `case_reel` | 0.1.0 | Case-study reklama | Qat'iy hikoya shabloni (hook → mijoz → muammo → strategiya → test → natija → xulosa → CTA), slot-roll hisoblagich, film-burn o'tish | [docs/case_reel.md](docs/case_reel.md) |
| `spotlight_word` | 0.1.0 | Talking-head intro va hikoya | Bittadan oq so'z, kalit so'z katta sariq glow bilan, tile o'tish, metafora split layout | [docs/spotlight_word.md](docs/spotlight_word.md) |
| `in_scene_type` | 0.1.0 | Bitta spiker, cut-away yo'q | Kadr ichida qatlamli matn (bosh orqasida yoki oldida), boshga bog'langan blok, zoom pulse, fizik o'tish | [docs/in_scene_type.md](docs/in_scene_type.md) |
| `holo_scene` | 0.1.0 | Spiker haqiqiy joyda brend, mahsulot yoki fakt haqida gapiradi | Stack titr (kalit so'z bosh orqasida), haqiqiy yuzalardagi cyan gologramma, bitta CGI sho'ng'ish, zarrachalardan yig'iladigan ekran | [docs/holo_scene.md](docs/holo_scene.md) |
| `editorial_showcase` | 0.1.0 | Spiker tushuntirishni haqiqiy ish, mahsulot yoki portfolio namoyishi bilan birlashtiradi | Serif + qisqa aksent, xabar/matn kartalari, hujjat sahnalari, pastki demo va uch qatorli namoyish | [docs/editorial_showcase.md](docs/editorial_showcase.md) |
| `ui_cascade` | 0.1.0 | Bitta spiker: ekspert, kreator, muammo va yechim haqida gapiradi | Harflab yig'iladigan stack titr va bitta magenta kalit so'z, 3D romb ikonkalar, shisha kartalar, to'liq ekranli ilova sahnalari (to-do, chat), kesimda negativ-flash | [docs/ui_cascade.md](docs/ui_cascade.md) |

## Qaysi uslubni tanlash

- Kadrda ikki yoki undan ko'p spiker bo'lsa (podkast, intervyu): `pod_glow`.
- Video natija haqidagi case study bo'lsa: `case_reel`.
- Spiker brend yoki agentlik nomidan gapirsa: `brand_stage`.
- Spiker faktlar va raqamlarni tushuntirsa: `talk_ahead`.
- Spiker o'zi, ishi yoki yo'li haqida gapirsa: `spotlight_word`.
- Spikerdan chiqmasdan, faqat kadr ichidagi matn va kamera bilan montaj kerak bo'lsa: `in_scene_type`.
- Spiker haqiqiy joyda gapirsa va har bir da'vo o'sha joyda gologramma bilan ko'rsatilishi kerak bo'lsa (premium agentlik uslubi): `holo_scene`.
- Tushuntirish va misollar/ish namoyishi navbatlashsa, editorial tipografika va demo panellari kerak bo'lsa: `editorial_showcase`. Yangi raw videoda hali sinalmagan; alohida engine renderer'i yo'q.
- Spiker muammo, jarayon yoki odatlar haqida tez va shijoatli gapirsa, sanalgan narsalar ikonka, jarayonlar esa ilova ekrani bo'lib ko'rsatilishi kerak bo'lsa: `ui_cascade`. Real videoda hali sinalmagan; alohida engine renderer'i yo'q.

Cheklov: 9 ta uslubning hammasi kadrda gapiradigan odam bo'lishini talab qiladi. Gapsiz B-roll montaj, spikersiz mahsulot videosi yoki faqat voiceover'li video uchun bu plaginda uslub yo'q.

## Tarkibi

```
styles/
├── .claude-plugin/plugin.json
├── README.md                 bu fayl
├── docs/<uslub>.md           har bir uslubning to'liq tavsifi va ma'lum cheklovlari
└── skills/<uslub>/
    ├── SKILL.md              uslub DNK'si va ish tartibi (2 ta tasdiq bosqichi bilan)
    └── references/*.md       beat-map, captions/type, devices, look, motion, sound, qa
```

## Manba

Skill'lar `D:\projects\higgsfield test01` ichidagi alohida plaginlardan (`talk_ahead`, `pod_glow`, `brand_stage`, `case_reel`, `spotlight_word`, `in_scene_type`) o'zgartirilmasdan nusxa qilingan. Eski papkalar 2026-11-05 da o'chirildi, endi asosiy nusxa shu plagin. Faqat `docs/` ichidagi ishga tushirish buyruqlari shu umumiy plaginga moslandi.
