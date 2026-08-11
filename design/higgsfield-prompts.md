# Higgsfield-промпты

> **Статус:** вызов Higgsfield (`generate_image`) в этой сессии оказался
> заблокирован на уровне коннектора («requires approval», не снималось
> даже после того, как пользователь подтвердил разрешение). Чтобы не
> оставлять срез недоделанным, все 4 актива ниже собраны вручную —
> favicon и заглушка фото как чистый SVG, OG-картинка и текстура как
> HTML/CSS, отрендеренные тем же Chromium через Playwright — по точно
> той же спецификации (цвета/шрифты/композиция), что описана в промптах.
> Результат лежит в `static/images/`. Промпты ниже остаются рабочими:
> когда Higgsfield будет доступен, можно сгенерировать более
> выразительные версии и просто заменить файлы с теми же именами —
> в шаблонах ничего менять не придётся.

Срез 5 плана. Направление зафиксировано в `DESIGN.md` — «Табло расписания»
(советско-российский информационный дизайн вокзальных табло): бумажно-белый
фон, чёрные чернила, один зарезервированный акцент — литургический красный,
никакого золота и завитушек.

⚠️ Правило проекта: **фото людей, духовенства и самого храма не генерируются**.
Везде, где сайту нужен такой снимок, стоит пустое поле в админке и плейсхолдер
в разделе «Что нужно снять» ниже — до реальной фотосъёмки эти поля остаются
пустыми, ничем не подменяются.

Из-за самого направления сайту не нужен декоративный hero-баннер — первый
экран главной страницы уже является «табло» (три ближайшие службы), это
осознанное решение дизайна, не пробел. Поэтому набор промптов здесь короче,
чем обычно просят под «шаг 4»: генерируется только то, что у сайта реально
функционально отсутствует — favicon, картинка для превью в соцсетях,
заглушка для пустой фотогалереи и лёгкая фоновая текстура для этих же мест.
Больше картинок = больше веса страницы, что прямо конфликтует с требованием
«быстрая загрузка».

## 1. Favicon / иконка сайта

**Модель:** nano_banana_pro (чёткий, высококонтрастный, текстовый/векторный рендер)
**Размер:** 512×512, квадрат, прозрачный или белый фон
**Промпт:**
```
Flat minimal icon of a plain three-bar Orthodox cross (russian orthodox
cross with slanted lower bar), pure black ink on white background, no
gradients, no gold, no ornamental swirls, no photorealism, geometric and
precise like a technical signage pictogram from a Soviet-era railway
departure board, thick even linework, centered, generous padding, square
composition, print-poster flat design
```

## 2. OG / превью для соцсетей

**Модель:** nano_banana_pro (умеет корректно рендерить текст)
**Размер:** 1200×630
**Промпт:**
```
Flat graphic design in the style of a Soviet-era railway departure board /
timetable sign: near-white paper background (#f7f7f5), near-black ink
(#17181a), one accent color deep vermillion red (#ac2b1e) used sparingly.
Bold geometric grotesk headline text "ПРИХОД БЛАГОВЕЩЕНИЯ ПРЕСВЯТОЙ
БОГОРОДИЦЫ" and smaller text "Джексонвиль, Флорида" below it. Below the
text, a graphic motif of abstract horizontal timetable rows (plain
rectangles and rule lines suggesting a schedule board, no real dates or
times written on them, purely abstract/generic bars). No photography, no
people, no building, no icons of saints, no gold ornament, flat print
design, high contrast, hard edges, no drop shadows, no rounded corners
```
Важно: на самом табло НЕ должно быть настоящих дат/служб — только
абстрактные полосы-заглушки, чтобы картинка не устаревала и не выдавала
себя за реальное расписание.

## 3. Заглушка «фото появится позже» (пустая фотогалерея)

Используется в галереях служений, стройки и школы, пока не загружены
реальные фото.

**Модель:** nano_banana_pro
**Размер:** 800×800, квадрат
**Промпт:**
```
Flat minimal icon in a square frame: simple outline of a picture/photo
frame with a small mountain-and-sun glyph inside (universal "image
placeholder" pictogram), thin even black linework on near-white
background (#f7f7f5), no color except optional thin vermillion red
(#ac2b1e) accent line on one edge of the frame, no photorealism, no
gradients, no gold, flat technical-signage style matching a railway
departure board pictogram set
```

## 4. Фоновая текстура (лёгкий орнамент)

Используется очень бледно (низкая непрозрачность) под hero-секцией
главной страницы и в футере — единственный «орнаментальный» элемент
дизайна, вместо золотых завитушек.

**Модель:** nano_banana_pro
**Размер:** 1024×1024, tileable (бесшовная по краям)
**Промпт:**
```
Seamless tileable background texture: extremely subtle grid of thin
horizontal ruled lines and faint tick marks, like graph paper or a
timetable printout, near-white (#f7f7f5) background, lines in a barely
visible light grey (#e4e4e1), no color, no photorealism, no gradients,
completely flat, very low contrast, meant to be used at low opacity as a
background texture, not a standalone graphic
```

## Что нужно снять (реальные фото — не генерировать)

Список для секретаря/фотографа прихода — этими полями в админке пока
никто не заполнен, там плейсхолдер:

- **Духовенство** (`core.ClergyMember.photo`) — портрет каждого клирика,
  нейтральный фон, вертикальный кадр.
- **Храм** — фасад снаружи, интерьер (иконостас, зал), для `core` about-страницы
  и общих hero-мест при появлении таких блоков.
- **Стройка** (`building.BuildingProjectPhoto`, `BuildingProjectUpdate.cover_image`) —
  регулярные фото хода строительства, «было/стало».
- **Русская школа** (`school.RussianSchoolPhoto`) — занятия, дети, педагоги
  (с согласия родителей на публикацию).
- **Служения** (`ministries.Ministry.image`, `MinistryPhoto`) — хор на
  клиросе, воскресная школа, трапезы и т.д., по одному фото на служение
  минимум.
- **Вехи истории** (`history.HistoryMilestone.image`) — архивные фото по
  возможности (первое здание, основатели, ранние богослужения) — если
  архивных фото нет, поле просто остаётся пустым, а не дорисовывается.
