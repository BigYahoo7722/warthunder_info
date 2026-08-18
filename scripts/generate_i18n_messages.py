#!/usr/bin/env python3
"""
generate_i18n_messages.py
===========================
Writes messages/{locale}.json for all 16 locales from one Python dict per
locale, keyed identically to the English source. Run this after editing any
locale's text below.

HONESTY NOTE ON TRANSLATION QUALITY — read this before shipping:
Every non-English string below is an AI-drafted first-pass translation, not
a professionally localized or native-speaker-reviewed one. For short,
low-ambiguity UI/technical vocabulary ("Top speed", "Mobility", "Reload
(base)") the risk of a genuinely wrong translation is low, but tone,
register, and natural phrasing can still be off in ways only a native
speaker will catch. Treat this as a working first draft for all 16 locales
alike — get a native-speaker pass before real production use, and treat the
two RTL locales (fa, ar) with extra scrutiny since they carry layout risk
(bidi text mixing with numbers, line-wrapping) on top of translation risk.

Usage: python3 scripts/generate_i18n_messages.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "messages"


def m(meta, header, hero, sidebar, category, nation, grid, modal, language):
    return {
        "meta": meta, "header": header, "hero": hero, "sidebar": sidebar,
        "category": category, "nation": nation, "grid": grid,
        "modal": modal, "language": language,
    }


MESSAGES: dict[str, dict] = {}

# --------------------------------------------------------------------- EN --
MESSAGES["en"] = m(
    meta={"title": "War Thunder Codex — Field Dossier",
          "description": "A complete, virtualized reference for the War Thunder vehicle roster."},
    header={"classified": "Classified — War Thunder Codex", "cover": "Cover"},
    hero={"eyebrow1": "Field Dossier · Combined Arms", "title1": "Every hull, airframe & hull number — catalogued.",
          "caption1": "2,600+ records indexed across ten nations.",
          "eyebrow2": "Clearance Level · Top Tier", "title2": "Rank VIII airframes, decoded to the avionics suite.",
          "caption2": "Radar bands, thermal generation, RWR — on file.",
          "eyebrow3": "Annex C · Fleet", "title3": "Coastal patrol to blue-water — every hull class.",
          "caption3": "Displacement, belt armor, AA suites cross-referenced."},
    sidebar={"navLabel": "Nation and vehicle category", "clearanceFiledUnder": "Clearance filed under",
             "selectPrompt": "Select a nation on the left to open its file."},
    category={"aviation": "Aviation", "army": "Army", "fleet": "Fleet", "helicopters": "Helicopters"},
    nation={"usa": "USA", "germany": "Germany", "ussr": "USSR", "britain": "Britain", "japan": "Japan",
            "china": "China", "italy": "Italy", "france": "France", "sweden": "Sweden", "israel": "Israel"},
    grid={"recordsLoaded": "{loaded} / {total} loaded", "noRecords": "No records filed under this heading.",
          "pullingChunk": "Pulling next chunk from archive…", "requestFailed": "Archive request failed",
          "requestFailedDetail": "The API route couldn't be reached. Check that the dev server is running."},
    modal={"close": "Close dossier", "rareAcquisition": "Rare acquisition", "eventExclusive": "Event exclusive",
           "arcade": "Arcade", "realistic": "Realistic", "simulator": "Simulator", "crew": "Crew",
           "repairRb": "Repair {value} SL (RB)", "slMultiplier": "SL ×{value}", "rpMultiplier": "RP ×{value}",
           "sectionMobility": "Mobility", "sectionFirepower": "Firepower", "sectionArmor": "Armor & survivability",
           "sectionAvionics": "Avionics", "sectionProTips": "Pro player tips",
           "secA": "Sec. A", "secB": "Sec. B", "secC": "Sec. C", "secD": "Sec. D", "fieldNotes": "Field notes",
           "power": "Power", "weight": "Weight", "powerToWeight": "Power/wt", "topSpeed": "Top speed",
           "reverse": "Reverse", "turnTime": "Turn time", "climb": "Climb", "transmission": "Transmission",
           "reloadBase": "Reload (base)", "reloadAced": "Reload (aced)", "vertTraverse": "Vert. traverse",
           "horizTraverse": "Horiz. traverse", "hullFront": "Hull front", "hullSide": "Hull side",
           "hullRear": "Hull rear", "turretFront": "Turret front", "turretSide": "Turret side",
           "turretRear": "Turret rear", "era": "ERA", "composite": "Composite", "fitted": "Fitted",
           "none": "None", "yes": "Yes", "no": "No", "radarRange": "Radar range", "thermal": "Thermal",
           "genN": "Gen {n}", "rwr": "RWR", "laserWarning": "Laser warning",
           "ballisticComputer": "Ballistic computer"},
    language={"label": "Language", "translateToggle": "Translate vehicle data", "translating": "Translating…",
              "translateError": "Translation unavailable — showing original text.",
              "needsApiKey": "Translation API key not configured."},
)

# --------------------------------------------------------------------- FA --
# RTL. "left"/"right" spatial references are adapted, not translated
# literally — the sidebar physically moves to the right under RTL, so
# selectPrompt says "right", matching the mirrored layout, not the English
# source's "left".
MESSAGES["fa"] = m(
    meta={"title": "War Thunder Codex — پرونده میدانی",
          "description": "مرجعی کامل و مجازی‌سازی‌شده برای کل فهرست وسایل نقلیه War Thunder."},
    header={"classified": "محرمانه — War Thunder Codex", "cover": "بازگشت"},
    hero={"eyebrow1": "پرونده میدانی · نیروهای ترکیبی", "title1": "هر بدنه، هر فروند و هر شماره بدنه — ثبت و طبقه‌بندی‌شده.",
          "caption1": "بیش از ۲٬۶۰۰ رکورد در ده کشور نمایه‌شده.",
          "eyebrow2": "سطح دسترسی · رتبه برتر", "title2": "هواپیماهای رتبه هشتم، تا سطح سامانه الکترونیک پرنده رمزگشایی‌شده.",
          "caption2": "برد رادار، نسل حرارتی، RWR — در پرونده.",
          "eyebrow3": "ضمیمه C · نیروی دریایی", "title3": "از گشت ساحلی تا آب‌های آزاد — هر رده بدنه.",
          "caption3": "آبخور، زره کمربندی و سامانه‌های پدافند هوایی مرجع‌گذاری‌شده."},
    sidebar={"navLabel": "کشور و دسته وسیله نقلیه", "clearanceFiledUnder": "پرونده تحت عنوان",
             "selectPrompt": "یک کشور را از سمت راست انتخاب کن تا پرونده‌اش باز شود."},
    category={"aviation": "هوایی", "army": "زمینی", "fleet": "دریایی", "helicopters": "بالگرد"},
    nation={"usa": "آمریکا", "germany": "آلمان", "ussr": "شوروی", "britain": "بریتانیا", "japan": "ژاپن",
            "china": "چین", "italy": "ایتالیا", "france": "فرانسه", "sweden": "سوئد", "israel": "اسرائیل"},
    grid={"recordsLoaded": "{loaded} از {total} بارگذاری‌شده", "noRecords": "رکوردی تحت این عنوان ثبت نشده.",
          "pullingChunk": "در حال دریافت بخش بعدی از آرشیو…", "requestFailed": "درخواست آرشیو ناموفق بود",
          "requestFailedDetail": "اتصال به API برقرار نشد. مطمئن شو سرور توسعه در حال اجراست."},
    modal={"close": "بستن پرونده", "rareAcquisition": "اکتساب کمیاب", "eventExclusive": "ویژه رویداد",
           "arcade": "آرکید", "realistic": "واقع‌گرایانه", "simulator": "شبیه‌ساز", "crew": "خدمه",
           "repairRb": "تعمیر {value} SL (RB)", "slMultiplier": "ضریب SL ×{value}", "rpMultiplier": "ضریب RP ×{value}",
           "sectionMobility": "تحرک", "sectionFirepower": "آتش‌قدرت", "sectionArmor": "زره و بقا",
           "sectionAvionics": "الکترونیک پرنده", "sectionProTips": "نکات حرفه‌ای",
           "secA": "بخش A", "secB": "بخش B", "secC": "بخش C", "secD": "بخش D", "fieldNotes": "یادداشت‌های میدانی",
           "power": "قدرت", "weight": "وزن", "powerToWeight": "قدرت به وزن", "topSpeed": "سرعت حداکثر",
           "reverse": "دنده عقب", "turnTime": "زمان چرخش", "climb": "نرخ صعود", "transmission": "گیربکس",
           "reloadBase": "بارگذاری مجدد (پایه)", "reloadAced": "بارگذاری مجدد (کامل)", "vertTraverse": "چرخش عمودی",
           "horizTraverse": "چرخش افقی", "hullFront": "جلوی بدنه", "hullSide": "پهلوی بدنه",
           "hullRear": "پشت بدنه", "turretFront": "جلوی برج", "turretSide": "پهلوی برج",
           "turretRear": "پشت برج", "era": "زره واکنشی (ERA)", "composite": "زره کامپوزیت", "fitted": "نصب‌شده",
           "none": "ندارد", "yes": "بله", "no": "خیر", "radarRange": "برد رادار", "thermal": "حرارتی",
           "genN": "نسل {n}", "rwr": "هشداردهنده رادار (RWR)", "laserWarning": "هشدار لیزر",
           "ballisticComputer": "رایانه بالستیک"},
    language={"label": "زبان", "translateToggle": "ترجمه اطلاعات وسیله نقلیه", "translating": "در حال ترجمه…",
              "translateError": "ترجمه در دسترس نیست — متن اصلی نمایش داده می‌شود.",
              "needsApiKey": "کلید API ترجمه تنظیم نشده است."},
)

# --------------------------------------------------------------------- AR --
MESSAGES["ar"] = m(
    meta={"title": "War Thunder Codex — الملف الميداني",
          "description": "مرجع كامل وقابل للتصغير الافتراضي لكامل قائمة مركبات War Thunder."},
    header={"classified": "سري للغاية — War Thunder Codex", "cover": "رجوع"},
    hero={"eyebrow1": "ملف ميداني · أسلحة مشتركة", "title1": "كل هيكل وطائرة ورقم هيكل — مُفهرَس.",
          "caption1": "أكثر من 2,600 سجل موزعة على عشر دول.",
          "eyebrow2": "مستوى التصريح · الفئة العليا", "title2": "طائرات الرتبة الثامنة، مفكوكة الشيفرة حتى منظومة الطيران الإلكتروني.",
          "caption2": "نطاقات الرادار، جيل الأشعة الحرارية، أجهزة الإنذار الراداري — في الملف.",
          "eyebrow3": "الملحق C · الأسطول", "title3": "من الدوريات الساحلية إلى المياه الزرقاء — كل فئة هيكل.",
          "caption3": "الإزاحة، درع الحزام، ومنظومات الدفاع الجوي — مرجعية متقاطعة."},
    sidebar={"navLabel": "الدولة وفئة المركبة", "clearanceFiledUnder": "الملف مصنّف تحت",
             "selectPrompt": "اختر دولة من اليمين لفتح ملفها."},
    category={"aviation": "طيران", "army": "جيش", "fleet": "أسطول", "helicopters": "مروحيات"},
    nation={"usa": "الولايات المتحدة", "germany": "ألمانيا", "ussr": "الاتحاد السوفيتي", "britain": "بريطانيا",
            "japan": "اليابان", "china": "الصين", "italy": "إيطاليا", "france": "فرنسا", "sweden": "السويد",
            "israel": "إسرائيل"},
    grid={"recordsLoaded": "{loaded} / {total} محمّل", "noRecords": "لا توجد سجلات مصنّفة تحت هذا العنوان.",
          "pullingChunk": "جارٍ سحب الجزء التالي من الأرشيف…", "requestFailed": "فشل طلب الأرشيف",
          "requestFailedDetail": "تعذّر الوصول إلى واجهة البرمجة. تأكد من تشغيل خادم التطوير."},
    modal={"close": "إغلاق الملف", "rareAcquisition": "اقتناء نادر", "eventExclusive": "حصري لفعالية",
           "arcade": "أركيد", "realistic": "واقعي", "simulator": "محاكاة", "crew": "الطاقم",
           "repairRb": "الإصلاح {value} SL (RB)", "slMultiplier": "مضاعف SL ×{value}", "rpMultiplier": "مضاعف RP ×{value}",
           "sectionMobility": "الحركة", "sectionFirepower": "القوة النارية", "sectionArmor": "الدرع والبقاء",
           "sectionAvionics": "الطيران الإلكتروني", "sectionProTips": "نصائح المحترفين",
           "secA": "القسم A", "secB": "القسم B", "secC": "القسم C", "secD": "القسم D", "fieldNotes": "ملاحظات ميدانية",
           "power": "القدرة", "weight": "الوزن", "powerToWeight": "القدرة/الوزن", "topSpeed": "السرعة القصوى",
           "reverse": "الرجوع للخلف", "turnTime": "زمن الدوران", "climb": "معدل الصعود", "transmission": "ناقل الحركة",
           "reloadBase": "إعادة التلقيم (أساسي)", "reloadAced": "إعادة التلقيم (كامل)", "vertTraverse": "الدوران الرأسي",
           "horizTraverse": "الدوران الأفقي", "hullFront": "مقدمة الهيكل", "hullSide": "جانب الهيكل",
           "hullRear": "مؤخرة الهيكل", "turretFront": "مقدمة البرج", "turretSide": "جانب البرج",
           "turretRear": "مؤخرة البرج", "era": "درع تفاعلي (ERA)", "composite": "درع مركب", "fitted": "مُركَّب",
           "none": "لا يوجد", "yes": "نعم", "no": "لا", "radarRange": "مدى الرادار", "thermal": "حراري",
           "genN": "الجيل {n}", "rwr": "جهاز إنذار راداري (RWR)", "laserWarning": "إنذار ليزر",
           "ballisticComputer": "حاسوب باليستي"},
    language={"label": "اللغة", "translateToggle": "ترجمة بيانات المركبة", "translating": "جارٍ الترجمة…",
              "translateError": "الترجمة غير متاحة — يُعرض النص الأصلي.",
              "needsApiKey": "لم يتم تكوين مفتاح API للترجمة."},
)

# --------------------------------------------------------------------- ES --
MESSAGES["es"] = m(
    meta={"title": "War Thunder Codex — Expediente de Campo",
          "description": "Una referencia completa y virtualizada para todo el catálogo de vehículos de War Thunder."},
    header={"classified": "Confidencial — War Thunder Codex", "cover": "Portada"},
    hero={"eyebrow1": "Expediente de Campo · Armas Combinadas", "title1": "Cada casco, aeronave y número de serie — catalogado.",
          "caption1": "Más de 2.600 registros indexados en diez naciones.",
          "eyebrow2": "Nivel de Acceso · Gama Alta", "title2": "Aeronaves de rango VIII, descifradas hasta la suite de aviónica.",
          "caption2": "Bandas de radar, generación térmica, RWR — en el expediente.",
          "eyebrow3": "Anexo C · Flota", "title3": "De patrulla costera a alta mar — cada clase de casco.",
          "caption3": "Desplazamiento, blindaje de cinturón y sistemas antiaéreos — referenciados."},
    sidebar={"navLabel": "Nación y categoría de vehículo", "clearanceFiledUnder": "Expediente archivado bajo",
             "selectPrompt": "Selecciona una nación a la izquierda para abrir su expediente."},
    category={"aviation": "Aviación", "army": "Ejército", "fleet": "Flota", "helicopters": "Helicópteros"},
    nation={"usa": "EE. UU.", "germany": "Alemania", "ussr": "URSS", "britain": "Gran Bretaña", "japan": "Japón",
            "china": "China", "italy": "Italia", "france": "Francia", "sweden": "Suecia", "israel": "Israel"},
    grid={"recordsLoaded": "{loaded} / {total} cargados", "noRecords": "No hay registros archivados bajo este apartado.",
          "pullingChunk": "Extrayendo el siguiente bloque del archivo…", "requestFailed": "Fallo en la solicitud al archivo",
          "requestFailedDetail": "No se pudo contactar con la ruta de la API. Comprueba que el servidor de desarrollo esté activo."},
    modal={"close": "Cerrar expediente", "rareAcquisition": "Adquisición rara", "eventExclusive": "Exclusivo de evento",
           "arcade": "Arcade", "realistic": "Realista", "simulator": "Simulador", "crew": "Tripulación",
           "repairRb": "Reparación {value} SL (RB)", "slMultiplier": "Multiplicador SL ×{value}", "rpMultiplier": "Multiplicador RP ×{value}",
           "sectionMobility": "Movilidad", "sectionFirepower": "Potencia de fuego", "sectionArmor": "Blindaje y supervivencia",
           "sectionAvionics": "Aviónica", "sectionProTips": "Consejos de expertos",
           "secA": "Sec. A", "secB": "Sec. B", "secC": "Sec. C", "secD": "Sec. D", "fieldNotes": "Notas de campo",
           "power": "Potencia", "weight": "Peso", "powerToWeight": "Potencia/peso", "topSpeed": "Velocidad máxima",
           "reverse": "Marcha atrás", "turnTime": "Tiempo de giro", "climb": "Régimen de ascenso", "transmission": "Transmisión",
           "reloadBase": "Recarga (base)", "reloadAced": "Recarga (as)", "vertTraverse": "Elevación vertical",
           "horizTraverse": "Giro horizontal", "hullFront": "Frontal del casco", "hullSide": "Lateral del casco",
           "hullRear": "Trasera del casco", "turretFront": "Frontal de la torreta", "turretSide": "Lateral de la torreta",
           "turretRear": "Trasera de la torreta", "era": "Blindaje reactivo (ERA)", "composite": "Blindaje compuesto", "fitted": "Instalado",
           "none": "Ninguno", "yes": "Sí", "no": "No", "radarRange": "Alcance del radar", "thermal": "Térmico",
           "genN": "Gen. {n}", "rwr": "Detector de radar (RWR)", "laserWarning": "Alerta láser",
           "ballisticComputer": "Computadora balística"},
    language={"label": "Idioma", "translateToggle": "Traducir datos del vehículo", "translating": "Traduciendo…",
              "translateError": "Traducción no disponible — se muestra el texto original.",
              "needsApiKey": "La clave de la API de traducción no está configurada."},
)

# --------------------------------------------------------------------- DE --
MESSAGES["de"] = m(
    meta={"title": "War Thunder Codex — Feldakte",
          "description": "Eine vollständige, virtualisierte Referenz für das gesamte War-Thunder-Fahrzeugregister."},
    header={"classified": "Geheim — War Thunder Codex", "cover": "Titelseite"},
    hero={"eyebrow1": "Feldakte · Kombinierte Waffen", "title1": "Jeder Rumpf, jedes Flugzeug, jede Fahrgestellnummer — erfasst.",
          "caption1": "Über 2.600 Einträge in zehn Nationen indiziert.",
          "eyebrow2": "Freigabestufe · Topklasse", "title2": "Flugzeuge der Rang-VIII-Klasse, bis zur Avionik-Suite entschlüsselt.",
          "caption2": "Radarreichweiten, Wärmebildgeneration, RWR — aktenkundig.",
          "eyebrow3": "Anhang C · Marine", "title3": "Von der Küstenpatrouille bis zur Hochsee — jede Schiffsklasse.",
          "caption3": "Verdrängung, Gürtelpanzerung und Flugabwehrsysteme — abgeglichen."},
    sidebar={"navLabel": "Nation und Fahrzeugkategorie", "clearanceFiledUnder": "Akte abgelegt unter",
             "selectPrompt": "Wähle links eine Nation, um ihre Akte zu öffnen."},
    category={"aviation": "Luftwaffe", "army": "Heer", "fleet": "Marine", "helicopters": "Hubschrauber"},
    nation={"usa": "USA", "germany": "Deutschland", "ussr": "UdSSR", "britain": "Großbritannien", "japan": "Japan",
            "china": "China", "italy": "Italien", "france": "Frankreich", "sweden": "Schweden", "israel": "Israel"},
    grid={"recordsLoaded": "{loaded} / {total} geladen", "noRecords": "Unter diesem Punkt sind keine Einträge erfasst.",
          "pullingChunk": "Nächster Abschnitt wird aus dem Archiv geladen…", "requestFailed": "Archivanfrage fehlgeschlagen",
          "requestFailedDetail": "Die API-Route konnte nicht erreicht werden. Prüfe, ob der Entwicklungsserver läuft."},
    modal={"close": "Akte schließen", "rareAcquisition": "Seltener Erwerb", "eventExclusive": "Event-exklusiv",
           "arcade": "Arcade", "realistic": "Realistisch", "simulator": "Simulator", "crew": "Besatzung",
           "repairRb": "Reparatur {value} SL (RB)", "slMultiplier": "SL-Multiplikator ×{value}", "rpMultiplier": "RP-Multiplikator ×{value}",
           "sectionMobility": "Mobilität", "sectionFirepower": "Feuerkraft", "sectionArmor": "Panzerung & Überlebensfähigkeit",
           "sectionAvionics": "Avionik", "sectionProTips": "Profi-Tipps",
           "secA": "Abschn. A", "secB": "Abschn. B", "secC": "Abschn. C", "secD": "Abschn. D", "fieldNotes": "Feldnotizen",
           "power": "Leistung", "weight": "Gewicht", "powerToWeight": "Leistungsgewicht", "topSpeed": "Höchstgeschwindigkeit",
           "reverse": "Rückwärtsgang", "turnTime": "Wendezeit", "climb": "Steigrate", "transmission": "Getriebe",
           "reloadBase": "Nachladezeit (Basis)", "reloadAced": "Nachladezeit (Ass)", "vertTraverse": "Vertikale Richtgeschwindigkeit",
           "horizTraverse": "Horizontale Richtgeschwindigkeit", "hullFront": "Wannenfront", "hullSide": "Wannenseite",
           "hullRear": "Wannenheck", "turretFront": "Turmfront", "turretSide": "Turmseite",
           "turretRear": "Turmheck", "era": "Reaktivpanzerung (ERA)", "composite": "Verbundpanzerung", "fitted": "Verbaut",
           "none": "Keine", "yes": "Ja", "no": "Nein", "radarRange": "Radarreichweite", "thermal": "Wärmebild",
           "genN": "Gen. {n}", "rwr": "Radarwarner (RWR)", "laserWarning": "Laserwarner",
           "ballisticComputer": "Ballistikrechner"},
    language={"label": "Sprache", "translateToggle": "Fahrzeugdaten übersetzen", "translating": "Wird übersetzt…",
              "translateError": "Übersetzung nicht verfügbar — Originaltext wird angezeigt.",
              "needsApiKey": "Kein API-Schlüssel für die Übersetzung konfiguriert."},
)

# --------------------------------------------------------------------- FR --
MESSAGES["fr"] = m(
    meta={"title": "War Thunder Codex — Dossier de terrain",
          "description": "Une référence complète et virtualisée pour l'ensemble du parc de véhicules de War Thunder."},
    header={"classified": "Confidentiel — War Thunder Codex", "cover": "Couverture"},
    hero={"eyebrow1": "Dossier de terrain · Armes combinées", "title1": "Chaque coque, chaque appareil, chaque numéro de série — répertorié.",
          "caption1": "Plus de 2 600 fiches indexées dans dix nations.",
          "eyebrow2": "Niveau d'habilitation · Haut de gamme", "title2": "Appareils de rang VIII, décryptés jusqu'à la suite avionique.",
          "caption2": "Portées radar, génération thermique, RWR — au dossier.",
          "eyebrow3": "Annexe C · Marine", "title3": "De la patrouille côtière à la haute mer — chaque classe de coque.",
          "caption3": "Déplacement, blindage de ceinture et systèmes antiaériens — recoupés."},
    sidebar={"navLabel": "Nation et catégorie de véhicule", "clearanceFiledUnder": "Dossier classé sous",
             "selectPrompt": "Choisis une nation à gauche pour ouvrir son dossier."},
    category={"aviation": "Aviation", "army": "Armée de terre", "fleet": "Marine", "helicopters": "Hélicoptères"},
    nation={"usa": "États-Unis", "germany": "Allemagne", "ussr": "URSS", "britain": "Grande-Bretagne", "japan": "Japon",
            "china": "Chine", "italy": "Italie", "france": "France", "sweden": "Suède", "israel": "Israël"},
    grid={"recordsLoaded": "{loaded} / {total} chargés", "noRecords": "Aucune fiche classée sous cette rubrique.",
          "pullingChunk": "Extraction du prochain lot depuis l'archive…", "requestFailed": "Échec de la requête d'archive",
          "requestFailedDetail": "Impossible de joindre la route API. Vérifie que le serveur de développement est lancé."},
    modal={"close": "Fermer le dossier", "rareAcquisition": "Acquisition rare", "eventExclusive": "Exclusif à un événement",
           "arcade": "Arcade", "realistic": "Réaliste", "simulator": "Simulateur", "crew": "Équipage",
           "repairRb": "Réparation {value} SL (RB)", "slMultiplier": "Multiplicateur SL ×{value}", "rpMultiplier": "Multiplicateur RP ×{value}",
           "sectionMobility": "Mobilité", "sectionFirepower": "Puissance de feu", "sectionArmor": "Blindage et survie",
           "sectionAvionics": "Avionique", "sectionProTips": "Astuces de pro",
           "secA": "Sect. A", "secB": "Sect. B", "secC": "Sect. C", "secD": "Sect. D", "fieldNotes": "Notes de terrain",
           "power": "Puissance", "weight": "Poids", "powerToWeight": "Puissance/poids", "topSpeed": "Vitesse max",
           "reverse": "Marche arrière", "turnTime": "Temps de virage", "climb": "Taux de montée", "transmission": "Transmission",
           "reloadBase": "Rechargement (base)", "reloadAced": "Rechargement (as)", "vertTraverse": "Pointage vertical",
           "horizTraverse": "Pointage horizontal", "hullFront": "Caisse avant", "hullSide": "Caisse latérale",
           "hullRear": "Caisse arrière", "turretFront": "Tourelle avant", "turretSide": "Tourelle latérale",
           "turretRear": "Tourelle arrière", "era": "Blindage réactif (ERA)", "composite": "Blindage composite", "fitted": "Installé",
           "none": "Aucun", "yes": "Oui", "no": "Non", "radarRange": "Portée radar", "thermal": "Thermique",
           "genN": "Gén. {n}", "rwr": "Détecteur radar (RWR)", "laserWarning": "Alerte laser",
           "ballisticComputer": "Calculateur balistique"},
    language={"label": "Langue", "translateToggle": "Traduire les données du véhicule", "translating": "Traduction en cours…",
              "translateError": "Traduction indisponible — texte original affiché.",
              "needsApiKey": "Clé API de traduction non configurée."},
)

# --------------------------------------------------------------------- IT --
MESSAGES["it"] = m(
    meta={"title": "War Thunder Codex — Dossier sul campo",
          "description": "Un riferimento completo e virtualizzato per l'intero elenco di veicoli di War Thunder."},
    header={"classified": "Riservato — War Thunder Codex", "cover": "Copertina"},
    hero={"eyebrow1": "Dossier sul campo · Armi combinate", "title1": "Ogni scafo, velivolo e numero di matricola — catalogato.",
          "caption1": "Oltre 2.600 schede indicizzate in dieci nazioni.",
          "eyebrow2": "Livello di accesso · Fascia alta", "title2": "Velivoli di rango VIII, decodificati fino alla suite avionica.",
          "caption2": "Portate radar, generazione termica, RWR — agli atti.",
          "eyebrow3": "Allegato C · Flotta", "title3": "Dalla pattuglia costiera all'alto mare — ogni classe di scafo.",
          "caption3": "Dislocamento, corazza di cintura e sistemi antiaerei — incrociati."},
    sidebar={"navLabel": "Nazione e categoria del veicolo", "clearanceFiledUnder": "Fascicolo archiviato sotto",
             "selectPrompt": "Seleziona una nazione a sinistra per aprire il suo fascicolo."},
    category={"aviation": "Aviazione", "army": "Esercito", "fleet": "Flotta", "helicopters": "Elicotteri"},
    nation={"usa": "USA", "germany": "Germania", "ussr": "URSS", "britain": "Gran Bretagna", "japan": "Giappone",
            "china": "Cina", "italy": "Italia", "france": "Francia", "sweden": "Svezia", "israel": "Israele"},
    grid={"recordsLoaded": "{loaded} / {total} caricati", "noRecords": "Nessuna scheda archiviata sotto questa voce.",
          "pullingChunk": "Recupero del prossimo blocco dall'archivio…", "requestFailed": "Richiesta all'archivio non riuscita",
          "requestFailedDetail": "Impossibile raggiungere la rotta API. Verifica che il server di sviluppo sia in esecuzione."},
    modal={"close": "Chiudi fascicolo", "rareAcquisition": "Acquisizione rara", "eventExclusive": "Esclusiva evento",
           "arcade": "Arcade", "realistic": "Realistico", "simulator": "Simulatore", "crew": "Equipaggio",
           "repairRb": "Riparazione {value} SL (RB)", "slMultiplier": "Moltiplicatore SL ×{value}", "rpMultiplier": "Moltiplicatore RP ×{value}",
           "sectionMobility": "Mobilità", "sectionFirepower": "Potenza di fuoco", "sectionArmor": "Corazza e sopravvivenza",
           "sectionAvionics": "Avionica", "sectionProTips": "Consigli da professionista",
           "secA": "Sez. A", "secB": "Sez. B", "secC": "Sez. C", "secD": "Sez. D", "fieldNotes": "Note sul campo",
           "power": "Potenza", "weight": "Peso", "powerToWeight": "Potenza/peso", "topSpeed": "Velocità massima",
           "reverse": "Retromarcia", "turnTime": "Tempo di virata", "climb": "Rateo di salita", "transmission": "Trasmissione",
           "reloadBase": "Ricarica (base)", "reloadAced": "Ricarica (asso)", "vertTraverse": "Puntamento verticale",
           "horizTraverse": "Puntamento orizzontale", "hullFront": "Scafo frontale", "hullSide": "Scafo laterale",
           "hullRear": "Scafo posteriore", "turretFront": "Torretta frontale", "turretSide": "Torretta laterale",
           "turretRear": "Torretta posteriore", "era": "Corazza reattiva (ERA)", "composite": "Corazza composita", "fitted": "Installata",
           "none": "Nessuna", "yes": "Sì", "no": "No", "radarRange": "Portata radar", "thermal": "Termico",
           "genN": "Gen. {n}", "rwr": "Rilevatore radar (RWR)", "laserWarning": "Allarme laser",
           "ballisticComputer": "Computer balistico"},
    language={"label": "Lingua", "translateToggle": "Traduci dati veicolo", "translating": "Traduzione in corso…",
              "translateError": "Traduzione non disponibile — viene mostrato il testo originale.",
              "needsApiKey": "Chiave API di traduzione non configurata."},
)

# --------------------------------------------------------------------- PT --
MESSAGES["pt"] = m(
    meta={"title": "War Thunder Codex — Dossiê de Campo",
          "description": "Uma referência completa e virtualizada para toda a frota de veículos do War Thunder."},
    header={"classified": "Confidencial — War Thunder Codex", "cover": "Capa"},
    hero={"eyebrow1": "Dossiê de Campo · Armas Combinadas", "title1": "Cada casco, aeronave e número de série — catalogado.",
          "caption1": "Mais de 2.600 registros indexados em dez nações.",
          "eyebrow2": "Nível de Acesso · Elite", "title2": "Aeronaves de patente VIII, decodificadas até a suíte de aviônica.",
          "caption2": "Alcances de radar, geração térmica, RWR — no arquivo.",
          "eyebrow3": "Anexo C · Frota", "title3": "Da patrulha costeira ao mar aberto — cada classe de casco.",
          "caption3": "Deslocamento, blindagem de cinturão e sistemas antiaéreos — referenciados."},
    sidebar={"navLabel": "Nação e categoria de veículo", "clearanceFiledUnder": "Dossiê arquivado sob",
             "selectPrompt": "Selecione uma nação à esquerda para abrir seu dossiê."},
    category={"aviation": "Aviação", "army": "Exército", "fleet": "Frota", "helicopters": "Helicópteros"},
    nation={"usa": "EUA", "germany": "Alemanha", "ussr": "URSS", "britain": "Grã-Bretanha", "japan": "Japão",
            "china": "China", "italy": "Itália", "france": "França", "sweden": "Suécia", "israel": "Israel"},
    grid={"recordsLoaded": "{loaded} / {total} carregados", "noRecords": "Nenhum registro arquivado sob este título.",
          "pullingChunk": "Buscando o próximo lote do arquivo…", "requestFailed": "Falha na solicitação ao arquivo",
          "requestFailedDetail": "Não foi possível acessar a rota da API. Verifique se o servidor de desenvolvimento está em execução."},
    modal={"close": "Fechar dossiê", "rareAcquisition": "Aquisição rara", "eventExclusive": "Exclusivo de evento",
           "arcade": "Arcade", "realistic": "Realista", "simulator": "Simulador", "crew": "Tripulação",
           "repairRb": "Reparo {value} SL (RB)", "slMultiplier": "Multiplicador SL ×{value}", "rpMultiplier": "Multiplicador RP ×{value}",
           "sectionMobility": "Mobilidade", "sectionFirepower": "Poder de fogo", "sectionArmor": "Blindagem e sobrevivência",
           "sectionAvionics": "Aviônica", "sectionProTips": "Dicas de profissionais",
           "secA": "Seç. A", "secB": "Seç. B", "secC": "Seç. C", "secD": "Seç. D", "fieldNotes": "Notas de campo",
           "power": "Potência", "weight": "Peso", "powerToWeight": "Potência/peso", "topSpeed": "Velocidade máxima",
           "reverse": "Marcha à ré", "turnTime": "Tempo de giro", "climb": "Taxa de subida", "transmission": "Transmissão",
           "reloadBase": "Recarga (base)", "reloadAced": "Recarga (ás)", "vertTraverse": "Mira vertical",
           "horizTraverse": "Mira horizontal", "hullFront": "Casco frontal", "hullSide": "Casco lateral",
           "hullRear": "Casco traseiro", "turretFront": "Torre frontal", "turretSide": "Torre lateral",
           "turretRear": "Torre traseira", "era": "Blindagem reativa (ERA)", "composite": "Blindagem composta", "fitted": "Instalada",
           "none": "Nenhuma", "yes": "Sim", "no": "Não", "radarRange": "Alcance do radar", "thermal": "Térmico",
           "genN": "Ger. {n}", "rwr": "Detector de radar (RWR)", "laserWarning": "Alerta a laser",
           "ballisticComputer": "Computador balístico"},
    language={"label": "Idioma", "translateToggle": "Traduzir dados do veículo", "translating": "Traduzindo…",
              "translateError": "Tradução indisponível — mostrando texto original.",
              "needsApiKey": "Chave de API de tradução não configurada."},
)

# --------------------------------------------------------------------- RU --
MESSAGES["ru"] = m(
    meta={"title": "War Thunder Codex — Полевое досье",
          "description": "Полный виртуализированный справочник по всему парку техники War Thunder."},
    header={"classified": "Секретно — War Thunder Codex", "cover": "Обложка"},
    hero={"eyebrow1": "Полевое досье · Общевойсковой", "title1": "Каждый корпус, самолёт и серийный номер — занесены в каталог.",
          "caption1": "Более 2600 записей по десяти странам.",
          "eyebrow2": "Уровень допуска · Высший ранг", "title2": "Самолёты VIII ранга, расшифрованные вплоть до авионики.",
          "caption2": "Дальность радара, поколение тепловизора, РЛС-предупреждение — в деле.",
          "eyebrow3": "Приложение C · Флот", "title3": "От прибрежного патруля до открытого моря — каждый класс корпуса.",
          "caption3": "Водоизмещение, поясная броня и системы ПВО — сверены."},
    sidebar={"navLabel": "Страна и категория техники", "clearanceFiledUnder": "Досье заведено на",
             "selectPrompt": "Выберите страну слева, чтобы открыть её досье."},
    category={"aviation": "Авиация", "army": "Наземные войска", "fleet": "Флот", "helicopters": "Вертолёты"},
    nation={"usa": "США", "germany": "Германия", "ussr": "СССР", "britain": "Великобритания", "japan": "Япония",
            "china": "Китай", "italy": "Италия", "france": "Франция", "sweden": "Швеция", "israel": "Израиль"},
    grid={"recordsLoaded": "{loaded} / {total} загружено", "noRecords": "По этому разделу записей не найдено.",
          "pullingChunk": "Загрузка следующего фрагмента архива…", "requestFailed": "Ошибка запроса к архиву",
          "requestFailedDetail": "Не удалось подключиться к маршруту API. Проверьте, запущен ли сервер разработки."},
    modal={"close": "Закрыть досье", "rareAcquisition": "Редкое приобретение", "eventExclusive": "Событийная техника",
           "arcade": "Аркада", "realistic": "Реалистичный", "simulator": "Симулятор", "crew": "Экипаж",
           "repairRb": "Ремонт {value} SL (RB)", "slMultiplier": "Множитель SL ×{value}", "rpMultiplier": "Множитель RP ×{value}",
           "sectionMobility": "Подвижность", "sectionFirepower": "Огневая мощь", "sectionArmor": "Броня и живучесть",
           "sectionAvionics": "Авионика", "sectionProTips": "Советы профи",
           "secA": "Разд. A", "secB": "Разд. B", "secC": "Разд. C", "secD": "Разд. D", "fieldNotes": "Полевые заметки",
           "power": "Мощность", "weight": "Масса", "powerToWeight": "Уд. мощность", "topSpeed": "Макс. скорость",
           "reverse": "Задний ход", "turnTime": "Время разворота", "climb": "Скороподъёмность", "transmission": "Трансмиссия",
           "reloadBase": "Перезарядка (базовая)", "reloadAced": "Перезарядка (эксперт)", "vertTraverse": "Верт. наводка",
           "horizTraverse": "Гориз. наводка", "hullFront": "Лоб корпуса", "hullSide": "Борт корпуса",
           "hullRear": "Корма корпуса", "turretFront": "Лоб башни", "turretSide": "Борт башни",
           "turretRear": "Корма башни", "era": "Динамическая защита (ERA)", "composite": "Композитная броня", "fitted": "Установлена",
           "none": "Нет", "yes": "Да", "no": "Нет", "radarRange": "Дальность радара", "thermal": "Тепловизор",
           "genN": "Пок. {n}", "rwr": "Станция предупреждения (РЛС)", "laserWarning": "Лазерное предупреждение",
           "ballisticComputer": "Баллистический вычислитель"},
    language={"label": "Язык", "translateToggle": "Перевести данные техники", "translating": "Перевод…",
              "translateError": "Перевод недоступен — показан исходный текст.",
              "needsApiKey": "Ключ API перевода не настроен."},
)

# --------------------------------------------------------------------- ZH --
MESSAGES["zh"] = m(
    meta={"title": "War Thunder Codex — 战地档案",
          "description": "War Thunder 全载具名录的完整虚拟化参考手册。"},
    header={"classified": "机密 — War Thunder Codex", "cover": "封面"},
    hero={"eyebrow1": "战地档案 · 诸兵种合成", "title1": "每一具车体、机体与编号——均已归档。",
          "caption1": "十个国家，超过 2,600 条记录已收录。",
          "eyebrow2": "许可等级 · 顶级", "title2": "八级机型，航电系统全面解密。",
          "caption2": "雷达范围、热成像代数、雷达告警——均已存档。",
          "eyebrow3": "附件 C · 舰船", "title3": "从近海巡逻到远洋作战——涵盖每一船级。",
          "caption3": "排水量、水线装甲与防空系统均已交叉核对。"},
    sidebar={"navLabel": "国家与载具类别", "clearanceFiledUnder": "档案归类于",
             "selectPrompt": "点击左侧国家以打开其档案。"},
    category={"aviation": "航空", "army": "陆军", "fleet": "舰船", "helicopters": "直升机"},
    nation={"usa": "美国", "germany": "德国", "ussr": "苏联", "britain": "英国", "japan": "日本",
            "china": "中国", "italy": "意大利", "france": "法国", "sweden": "瑞典", "israel": "以色列"},
    grid={"recordsLoaded": "已加载 {loaded} / {total}", "noRecords": "此分类下暂无记录。",
          "pullingChunk": "正在从档案库读取下一批数据…", "requestFailed": "档案请求失败",
          "requestFailedDetail": "无法连接到 API 路由，请确认开发服务器正在运行。"},
    modal={"close": "关闭档案", "rareAcquisition": "稀有获取", "eventExclusive": "活动限定",
           "arcade": "街机", "realistic": "现实", "simulator": "模拟", "crew": "乘员",
           "repairRb": "维修费 {value} SL（RB）", "slMultiplier": "SL 倍率 ×{value}", "rpMultiplier": "RP 倍率 ×{value}",
           "sectionMobility": "机动性", "sectionFirepower": "火力", "sectionArmor": "装甲与生存性",
           "sectionAvionics": "航电系统", "sectionProTips": "高手心得",
           "secA": "A 节", "secB": "B 节", "secC": "C 节", "secD": "D 节", "fieldNotes": "战地笔记",
           "power": "功率", "weight": "重量", "powerToWeight": "功重比", "topSpeed": "最高速度",
           "reverse": "倒车速度", "turnTime": "转向时间", "climb": "爬升率", "transmission": "变速箱",
           "reloadBase": "装填时间（基础）", "reloadAced": "装填时间（满编）", "vertTraverse": "垂直转速",
           "horizTraverse": "水平转速", "hullFront": "车体正面", "hullSide": "车体侧面",
           "hullRear": "车体后部", "turretFront": "炮塔正面", "turretSide": "炮塔侧面",
           "turretRear": "炮塔后部", "era": "反应装甲（ERA）", "composite": "复合装甲", "fitted": "已装备",
           "none": "无", "yes": "是", "no": "否", "radarRange": "雷达范围", "thermal": "热成像",
           "genN": "第 {n} 代", "rwr": "雷达告警装置（RWR）", "laserWarning": "激光告警",
           "ballisticComputer": "弹道计算机"},
    language={"label": "语言", "translateToggle": "翻译载具数据", "translating": "翻译中…",
              "translateError": "翻译不可用——显示原文。",
              "needsApiKey": "未配置翻译 API 密钥。"},
)

# --------------------------------------------------------------------- JA --
MESSAGES["ja"] = m(
    meta={"title": "War Thunder Codex — 野戦資料",
          "description": "War Thunder の全車両リストを網羅した仮想化リファレンス。"},
    header={"classified": "機密 — War Thunder Codex", "cover": "表紙"},
    hero={"eyebrow1": "野戦資料 · 諸兵科連合", "title1": "すべての車体・機体・登録番号を網羅。",
          "caption1": "10か国、2,600件以上のレコードを索引化。",
          "eyebrow2": "アクセスレベル · トップティア", "title2": "ランクVIII機、アビオニクスまで完全解析。",
          "caption2": "レーダー探知距離、赤外線世代、RWR — 記録済み。",
          "eyebrow3": "付属書C · 艦艇", "title3": "沿岸警備から外洋まで — 全艦種を網羅。",
          "caption3": "排水量、舷側装甲、対空システムを相互参照。"},
    sidebar={"navLabel": "国家と車両カテゴリー", "clearanceFiledUnder": "分類区分",
             "selectPrompt": "左側の国家を選択してファイルを開く。"},
    category={"aviation": "航空", "army": "陸軍", "fleet": "艦艇", "helicopters": "ヘリコプター"},
    nation={"usa": "アメリカ", "germany": "ドイツ", "ussr": "ソ連", "britain": "イギリス", "japan": "日本",
            "china": "中国", "italy": "イタリア", "france": "フランス", "sweden": "スウェーデン", "israel": "イスラエル"},
    grid={"recordsLoaded": "{loaded} / {total} 件読み込み済み", "noRecords": "この項目に該当する記録はありません。",
          "pullingChunk": "アーカイブから次のチャンクを取得中…", "requestFailed": "アーカイブへのリクエストに失敗",
          "requestFailedDetail": "APIルートに接続できませんでした。開発サーバーが起動しているか確認してください。"},
    modal={"close": "資料を閉じる", "rareAcquisition": "希少な入手経路", "eventExclusive": "イベント限定",
           "arcade": "アーケード", "realistic": "リアリスティック", "simulator": "シミュレーター", "crew": "乗員数",
           "repairRb": "修理費 {value} SL（RB）", "slMultiplier": "SL倍率 ×{value}", "rpMultiplier": "RP倍率 ×{value}",
           "sectionMobility": "機動性", "sectionFirepower": "火力", "sectionArmor": "装甲と生存性",
           "sectionAvionics": "アビオニクス", "sectionProTips": "プロのコツ",
           "secA": "第A項", "secB": "第B項", "secC": "第C項", "secD": "第D項", "fieldNotes": "現場メモ",
           "power": "出力", "weight": "重量", "powerToWeight": "パワーウェイトレシオ", "topSpeed": "最高速度",
           "reverse": "後退速度", "turnTime": "旋回時間", "climb": "上昇率", "transmission": "変速機",
           "reloadBase": "装填時間（基本）", "reloadAced": "装填時間（エース）", "vertTraverse": "俯仰速度",
           "horizTraverse": "旋回速度", "hullFront": "車体正面", "hullSide": "車体側面",
           "hullRear": "車体後面", "turretFront": "砲塔正面", "turretSide": "砲塔側面",
           "turretRear": "砲塔後面", "era": "リアクティブアーマー（ERA）", "composite": "複合装甲", "fitted": "装備済み",
           "none": "なし", "yes": "はい", "no": "いいえ", "radarRange": "レーダー探知距離", "thermal": "熱線暗視装置",
           "genN": "第{n}世代", "rwr": "レーダー警戒装置（RWR）", "laserWarning": "レーザー警報",
           "ballisticComputer": "弾道計算機"},
    language={"label": "言語", "translateToggle": "車両データを翻訳", "translating": "翻訳中…",
              "translateError": "翻訳は利用できません — 原文を表示しています。",
              "needsApiKey": "翻訳APIキーが設定されていません。"},
)

# --------------------------------------------------------------------- KO --
MESSAGES["ko"] = m(
    meta={"title": "War Thunder Codex — 야전 기록",
          "description": "War Thunder 전체 차량 목록을 위한 완전한 가상화 참고 자료."},
    header={"classified": "기밀 — War Thunder Codex", "cover": "표지"},
    hero={"eyebrow1": "야전 기록 · 제병협동", "title1": "모든 차체, 기체, 등록번호 — 전부 목록화됨.",
          "caption1": "10개국, 2,600건 이상의 기록이 색인됨.",
          "eyebrow2": "접근 등급 · 최상위 티어", "title2": "8랭크 기체, 항전장비까지 완전 해독.",
          "caption2": "레이더 탐지거리, 열영상 세대, RWR — 기록 완료.",
          "eyebrow3": "부록 C · 함대", "title3": "연안 순찰부터 대양까지 — 모든 함급 포함.",
          "caption3": "배수량, 측면 장갑, 대공 체계까지 상호 대조 완료."},
    sidebar={"navLabel": "국가 및 차량 분류", "clearanceFiledUnder": "분류 항목",
             "selectPrompt": "왼쪽에서 국가를 선택해 파일을 열어보세요."},
    category={"aviation": "항공", "army": "육군", "fleet": "함대", "helicopters": "헬리콥터"},
    nation={"usa": "미국", "germany": "독일", "ussr": "소련", "britain": "영국", "japan": "일본",
            "china": "중국", "italy": "이탈리아", "france": "프랑스", "sweden": "스웨덴", "israel": "이스라엘"},
    grid={"recordsLoaded": "{loaded} / {total} 로드됨", "noRecords": "이 항목에 등록된 기록이 없습니다.",
          "pullingChunk": "아카이브에서 다음 데이터 묶음을 가져오는 중…", "requestFailed": "아카이브 요청 실패",
          "requestFailedDetail": "API 경로에 연결할 수 없습니다. 개발 서버가 실행 중인지 확인하세요."},
    modal={"close": "파일 닫기", "rareAcquisition": "희귀 획득", "eventExclusive": "이벤트 한정",
           "arcade": "아케이드", "realistic": "리얼리스틱", "simulator": "시뮬레이터", "crew": "승무원",
           "repairRb": "수리비 {value} SL(RB)", "slMultiplier": "SL 배율 ×{value}", "rpMultiplier": "RP 배율 ×{value}",
           "sectionMobility": "기동성", "sectionFirepower": "화력", "sectionArmor": "장갑 및 생존성",
           "sectionAvionics": "항전장비", "sectionProTips": "프로 팁",
           "secA": "A절", "secB": "B절", "secC": "C절", "secD": "D절", "fieldNotes": "현장 노트",
           "power": "출력", "weight": "중량", "powerToWeight": "출력 대 중량비", "topSpeed": "최고 속도",
           "reverse": "후진 속도", "turnTime": "선회 시간", "climb": "상승률", "transmission": "변속기",
           "reloadBase": "재장전(기본)", "reloadAced": "재장전(에이스)", "vertTraverse": "수직 조준 속도",
           "horizTraverse": "수평 조준 속도", "hullFront": "차체 정면", "hullSide": "차체 측면",
           "hullRear": "차체 후면", "turretFront": "포탑 정면", "turretSide": "포탑 측면",
           "turretRear": "포탑 후면", "era": "반응장갑(ERA)", "composite": "복합장갑", "fitted": "장착됨",
           "none": "없음", "yes": "예", "no": "아니오", "radarRange": "레이더 탐지거리", "thermal": "열영상",
           "genN": "{n}세대", "rwr": "레이더 경보 수신기(RWR)", "laserWarning": "레이저 경보",
           "ballisticComputer": "탄도 계산기"},
    language={"label": "언어", "translateToggle": "차량 데이터 번역", "translating": "번역 중…",
              "translateError": "번역을 사용할 수 없습니다 — 원문을 표시합니다.",
              "needsApiKey": "번역 API 키가 설정되지 않았습니다."},
)

# --------------------------------------------------------------------- HI --
MESSAGES["hi"] = m(
    meta={"title": "War Thunder Codex — फ़ील्ड डोज़ियर",
          "description": "War Thunder की पूरी वाहन सूची के लिए एक संपूर्ण, वर्चुअलाइज़्ड संदर्भ।"},
    header={"classified": "गोपनीय — War Thunder Codex", "cover": "आवरण"},
    hero={"eyebrow1": "फ़ील्ड डोज़ियर · संयुक्त शस्त्र", "title1": "हर हल, हर विमान और हर पहचान संख्या — सूचीबद्ध।",
          "caption1": "दस देशों में 2,600+ रिकॉर्ड अनुक्रमित।",
          "eyebrow2": "क्लीयरेंस स्तर · शीर्ष श्रेणी", "title2": "रैंक VIII विमान, एवियॉनिक्स सुइट तक डिकोड किए गए।",
          "caption2": "रडार रेंज, थर्मल जनरेशन, RWR — फ़ाइल में दर्ज।",
          "eyebrow3": "अनुबंध C · बेड़ा", "title3": "तटीय गश्त से लेकर गहरे समुद्र तक — हर श्रेणी का पोत।",
          "caption3": "विस्थापन, बेल्ट कवच और वायु-रक्षा प्रणालियाँ — परस्पर सत्यापित।"},
    sidebar={"navLabel": "देश और वाहन श्रेणी", "clearanceFiledUnder": "फ़ाइल इसके अंतर्गत दर्ज",
             "selectPrompt": "फ़ाइल खोलने के लिए बाईं ओर से एक देश चुनें।"},
    category={"aviation": "विमानन", "army": "थल सेना", "fleet": "बेड़ा", "helicopters": "हेलीकॉप्टर"},
    nation={"usa": "अमेरिका", "germany": "जर्मनी", "ussr": "सोवियत संघ", "britain": "ब्रिटेन", "japan": "जापान",
            "china": "चीन", "italy": "इटली", "france": "फ़्रांस", "sweden": "स्वीडन", "israel": "इज़राइल"},
    grid={"recordsLoaded": "{loaded} / {total} लोड हुए", "noRecords": "इस श्रेणी में कोई रिकॉर्ड दर्ज नहीं है।",
          "pullingChunk": "अभिलेखागार से अगला भाग लाया जा रहा है…", "requestFailed": "अभिलेखागार अनुरोध विफल",
          "requestFailedDetail": "API रूट से संपर्क नहीं हो सका। जांचें कि डेव सर्वर चल रहा है या नहीं।"},
    modal={"close": "फ़ाइल बंद करें", "rareAcquisition": "दुर्लभ अधिग्रहण", "eventExclusive": "इवेंट-विशेष",
           "arcade": "आर्केड", "realistic": "रियलिस्टिक", "simulator": "सिम्युलेटर", "crew": "चालक दल",
           "repairRb": "मरम्मत {value} SL (RB)", "slMultiplier": "SL गुणक ×{value}", "rpMultiplier": "RP गुणक ×{value}",
           "sectionMobility": "गतिशीलता", "sectionFirepower": "फायरपावर", "sectionArmor": "कवच और उत्तरजीविता",
           "sectionAvionics": "एवियॉनिक्स", "sectionProTips": "प्रो टिप्स",
           "secA": "खंड A", "secB": "खंड B", "secC": "खंड C", "secD": "खंड D", "fieldNotes": "फ़ील्ड नोट्स",
           "power": "शक्ति", "weight": "वज़न", "powerToWeight": "शक्ति/वज़न", "topSpeed": "अधिकतम गति",
           "reverse": "रिवर्स गति", "turnTime": "मोड़ समय", "climb": "चढ़ाई दर", "transmission": "ट्रांसमिशन",
           "reloadBase": "रीलोड (बेस)", "reloadAced": "रीलोड (एस्ड)", "vertTraverse": "ऊर्ध्वाधर ट्रैवर्स",
           "horizTraverse": "क्षैतिज ट्रैवर्स", "hullFront": "हल फ्रंट", "hullSide": "हल साइड",
           "hullRear": "हल रियर", "turretFront": "बुर्ज फ्रंट", "turretSide": "बुर्ज साइड",
           "turretRear": "बुर्ज रियर", "era": "रिएक्टिव आर्मर (ERA)", "composite": "कम्पोज़िट आर्मर", "fitted": "लगा हुआ",
           "none": "कोई नहीं", "yes": "हाँ", "no": "नहीं", "radarRange": "रडार रेंज", "thermal": "थर्मल",
           "genN": "जनरेशन {n}", "rwr": "रडार चेतावनी रिसीवर (RWR)", "laserWarning": "लेज़र चेतावनी",
           "ballisticComputer": "बैलिस्टिक कंप्यूटर"},
    language={"label": "भाषा", "translateToggle": "वाहन डेटा अनुवादित करें", "translating": "अनुवाद हो रहा है…",
              "translateError": "अनुवाद उपलब्ध नहीं — मूल पाठ दिखाया जा रहा है।",
              "needsApiKey": "अनुवाद API कुंजी कॉन्फ़िगर नहीं की गई है।"},
)

# --------------------------------------------------------------------- TR --
MESSAGES["tr"] = m(
    meta={"title": "War Thunder Codex — Saha Dosyası",
          "description": "War Thunder'ın tüm araç listesi için eksiksiz, sanallaştırılmış bir referans."},
    header={"classified": "Gizli — War Thunder Codex", "cover": "Kapak"},
    hero={"eyebrow1": "Saha Dosyası · Birleşik Silahlar", "title1": "Her gövde, uçak ve şasi numarası — kataloglandı.",
          "caption1": "On ulusta 2.600'den fazla kayıt indekslendi.",
          "eyebrow2": "Yetki Seviyesi · Üst Sınıf", "title2": "Rütbe VIII uçaklar, aviyonik takımına kadar çözüldü.",
          "caption2": "Radar menzilleri, termal nesil, RWR — dosyada.",
          "eyebrow3": "Ek C · Filo", "title3": "Sahil devriyesinden açık denize — her gövde sınıfı.",
          "caption3": "Deplasman, kemer zırhı ve hava savunma sistemleri karşılaştırıldı."},
    sidebar={"navLabel": "Ulus ve araç kategorisi", "clearanceFiledUnder": "Dosya şu başlık altında",
             "selectPrompt": "Dosyasını açmak için soldan bir ulus seç."},
    category={"aviation": "Havacılık", "army": "Kara Kuvvetleri", "fleet": "Filo", "helicopters": "Helikopterler"},
    nation={"usa": "ABD", "germany": "Almanya", "ussr": "SSCB", "britain": "Britanya", "japan": "Japonya",
            "china": "Çin", "italy": "İtalya", "france": "Fransa", "sweden": "İsveç", "israel": "İsrail"},
    grid={"recordsLoaded": "{loaded} / {total} yüklendi", "noRecords": "Bu başlık altında kayıt bulunmuyor.",
          "pullingChunk": "Arşivden bir sonraki parça alınıyor…", "requestFailed": "Arşiv isteği başarısız oldu",
          "requestFailedDetail": "API rotasına ulaşılamadı. Geliştirme sunucusunun çalıştığından emin ol."},
    modal={"close": "Dosyayı kapat", "rareAcquisition": "Nadir edinim", "eventExclusive": "Etkinliğe özel",
           "arcade": "Arcade", "realistic": "Gerçekçi", "simulator": "Simülatör", "crew": "Mürettebat",
           "repairRb": "Onarım {value} SL (RB)", "slMultiplier": "SL çarpanı ×{value}", "rpMultiplier": "RP çarpanı ×{value}",
           "sectionMobility": "Hareket kabiliyeti", "sectionFirepower": "Ateş gücü", "sectionArmor": "Zırh ve hayatta kalma",
           "sectionAvionics": "Aviyonik", "sectionProTips": "Profesyonel ipuçları",
           "secA": "Böl. A", "secB": "Böl. B", "secC": "Böl. C", "secD": "Böl. D", "fieldNotes": "Saha notları",
           "power": "Güç", "weight": "Ağırlık", "powerToWeight": "Güç/ağırlık", "topSpeed": "Azami hız",
           "reverse": "Geri vites", "turnTime": "Dönüş süresi", "climb": "Tırmanma oranı", "transmission": "Şanzıman",
           "reloadBase": "Yeniden doldurma (temel)", "reloadAced": "Yeniden doldurma (usta)", "vertTraverse": "Dikey nişan hızı",
           "horizTraverse": "Yatay nişan hızı", "hullFront": "Gövde ön", "hullSide": "Gövde yan",
           "hullRear": "Gövde arka", "turretFront": "Taret ön", "turretSide": "Taret yan",
           "turretRear": "Taret arka", "era": "Reaktif zırh (ERA)", "composite": "Kompozit zırh", "fitted": "Takılı",
           "none": "Yok", "yes": "Evet", "no": "Hayır", "radarRange": "Radar menzili", "thermal": "Termal",
           "genN": "Nesil {n}", "rwr": "Radar uyarı alıcısı (RWR)", "laserWarning": "Lazer uyarısı",
           "ballisticComputer": "Balistik bilgisayar"},
    language={"label": "Dil", "translateToggle": "Araç verisini çevir", "translating": "Çevriliyor…",
              "translateError": "Çeviri kullanılamıyor — orijinal metin gösteriliyor.",
              "needsApiKey": "Çeviri API anahtarı yapılandırılmamış."},
)

# --------------------------------------------------------------------- VI --
MESSAGES["vi"] = m(
    meta={"title": "War Thunder Codex — Hồ Sơ Thực Địa",
          "description": "Tài liệu tham khảo đầy đủ, ảo hóa cho toàn bộ danh sách phương tiện War Thunder."},
    header={"classified": "Tuyệt mật — War Thunder Codex", "cover": "Trang bìa"},
    hero={"eyebrow1": "Hồ Sơ Thực Địa · Binh Chủng Hợp Thành", "title1": "Mọi thân xe, khung máy bay và số hiệu — đã được ghi danh.",
          "caption1": "Hơn 2.600 hồ sơ được lập chỉ mục trên mười quốc gia.",
          "eyebrow2": "Cấp Độ Truy Cập · Hạng Cao Nhất", "title2": "Máy bay Rank VIII, giải mã đến hệ thống điện tử hàng không.",
          "caption2": "Tầm radar, thế hệ ảnh nhiệt, RWR — đã lưu hồ sơ.",
          "eyebrow3": "Phụ Lục C · Hải Quân", "title3": "Từ tuần tra ven biển đến biển khơi — mọi lớp tàu.",
          "caption3": "Lượng giãn nước, giáp đai và hệ thống phòng không đã được đối chiếu."},
    sidebar={"navLabel": "Quốc gia và loại phương tiện", "clearanceFiledUnder": "Hồ sơ được xếp dưới mục",
             "selectPrompt": "Chọn một quốc gia bên trái để mở hồ sơ."},
    category={"aviation": "Không quân", "army": "Lục quân", "fleet": "Hải quân", "helicopters": "Trực thăng"},
    nation={"usa": "Hoa Kỳ", "germany": "Đức", "ussr": "Liên Xô", "britain": "Anh", "japan": "Nhật Bản",
            "china": "Trung Quốc", "italy": "Ý", "france": "Pháp", "sweden": "Thụy Điển", "israel": "Israel"},
    grid={"recordsLoaded": "Đã tải {loaded} / {total}", "noRecords": "Không có hồ sơ nào dưới mục này.",
          "pullingChunk": "Đang lấy phần dữ liệu tiếp theo từ kho lưu trữ…", "requestFailed": "Yêu cầu kho lưu trữ thất bại",
          "requestFailedDetail": "Không thể kết nối tới API. Kiểm tra xem máy chủ phát triển có đang chạy không."},
    modal={"close": "Đóng hồ sơ", "rareAcquisition": "Vật phẩm hiếm", "eventExclusive": "Độc quyền sự kiện",
           "arcade": "Arcade", "realistic": "Realistic", "simulator": "Simulator", "crew": "Kíp lái",
           "repairRb": "Sửa chữa {value} SL (RB)", "slMultiplier": "Hệ số SL ×{value}", "rpMultiplier": "Hệ số RP ×{value}",
           "sectionMobility": "Cơ động", "sectionFirepower": "Hỏa lực", "sectionArmor": "Giáp và khả năng sống sót",
           "sectionAvionics": "Điện tử hàng không", "sectionProTips": "Mẹo từ chuyên gia",
           "secA": "Mục A", "secB": "Mục B", "secC": "Mục C", "secD": "Mục D", "fieldNotes": "Ghi chú thực địa",
           "power": "Công suất", "weight": "Trọng lượng", "powerToWeight": "Tỷ lệ công suất/trọng lượng", "topSpeed": "Tốc độ tối đa",
           "reverse": "Tốc độ lùi", "turnTime": "Thời gian quay", "climb": "Tốc độ lên cao", "transmission": "Hộp số",
           "reloadBase": "Nạp đạn (cơ bản)", "reloadAced": "Nạp đạn (kíp lái xuất sắc)", "vertTraverse": "Tốc độ ngắm dọc",
           "horizTraverse": "Tốc độ ngắm ngang", "hullFront": "Giáp trước thân", "hullSide": "Giáp hông thân",
           "hullRear": "Giáp sau thân", "turretFront": "Giáp trước tháp pháo", "turretSide": "Giáp hông tháp pháo",
           "turretRear": "Giáp sau tháp pháo", "era": "Giáp phản ứng nổ (ERA)", "composite": "Giáp composite", "fitted": "Đã trang bị",
           "none": "Không có", "yes": "Có", "no": "Không", "radarRange": "Tầm radar", "thermal": "Ảnh nhiệt",
           "genN": "Thế hệ {n}", "rwr": "Thiết bị cảnh báo radar (RWR)", "laserWarning": "Cảnh báo laser",
           "ballisticComputer": "Máy tính đạn đạo"},
    language={"label": "Ngôn ngữ", "translateToggle": "Dịch dữ liệu phương tiện", "translating": "Đang dịch…",
              "translateError": "Không có bản dịch — hiển thị văn bản gốc.",
              "needsApiKey": "Chưa cấu hình khóa API dịch thuật."},
)

# --------------------------------------------------------------------- PL --
MESSAGES["pl"] = m(
    meta={"title": "War Thunder Codex — Dossier Polowe",
          "description": "Kompletne, zwirtualizowane źródło informacji o całej liście pojazdów War Thunder."},
    header={"classified": "Tajne — War Thunder Codex", "cover": "Okładka"},
    hero={"eyebrow1": "Dossier Polowe · Broń Połączona", "title1": "Każdy kadłub, płatowiec i numer seryjny — skatalogowany.",
          "caption1": "Ponad 2600 rekordów zindeksowanych w dziesięciu narodach.",
          "eyebrow2": "Poziom Dostępu · Najwyższa Klasa", "title2": "Samoloty rangi VIII, rozszyfrowane aż po awionikę.",
          "caption2": "Zasięgi radaru, generacja termowizji, RWR — w aktach.",
          "eyebrow3": "Aneks C · Flota", "title3": "Od patrolu przybrzeżnego po pełne morze — każda klasa kadłuba.",
          "caption3": "Wyporność, opancerzenie burtowe i systemy PLOT — zweryfikowane krzyżowo."},
    sidebar={"navLabel": "Nacja i kategoria pojazdu", "clearanceFiledUnder": "Akta prowadzone pod hasłem",
             "selectPrompt": "Wybierz nację po lewej, aby otworzyć jej akta."},
    category={"aviation": "Lotnictwo", "army": "Wojska lądowe", "fleet": "Flota", "helicopters": "Śmigłowce"},
    nation={"usa": "USA", "germany": "Niemcy", "ussr": "ZSRR", "britain": "Wielka Brytania", "japan": "Japonia",
            "china": "Chiny", "italy": "Włochy", "france": "Francja", "sweden": "Szwecja", "israel": "Izrael"},
    grid={"recordsLoaded": "Wczytano {loaded} / {total}", "noRecords": "Brak rekordów w tej kategorii.",
          "pullingChunk": "Pobieranie kolejnej partii z archiwum…", "requestFailed": "Żądanie do archiwum nie powiodło się",
          "requestFailedDetail": "Nie udało się połączyć z trasą API. Sprawdź, czy serwer deweloperski jest uruchomiony."},
    modal={"close": "Zamknij akta", "rareAcquisition": "Rzadkie nabytek", "eventExclusive": "Ekskluzywny wydarzeniowy",
           "arcade": "Arcade", "realistic": "Realistyczny", "simulator": "Symulator", "crew": "Załoga",
           "repairRb": "Naprawa {value} SL (RB)", "slMultiplier": "Mnożnik SL ×{value}", "rpMultiplier": "Mnożnik RP ×{value}",
           "sectionMobility": "Mobilność", "sectionFirepower": "Siła ognia", "sectionArmor": "Pancerz i przeżywalność",
           "sectionAvionics": "Awionika", "sectionProTips": "Porady ekspertów",
           "secA": "Sek. A", "secB": "Sek. B", "secC": "Sek. C", "secD": "Sek. D", "fieldNotes": "Notatki polowe",
           "power": "Moc", "weight": "Masa", "powerToWeight": "Moc/masa", "topSpeed": "Prędkość maksymalna",
           "reverse": "Prędkość wsteczna", "turnTime": "Czas obrotu", "climb": "Prędkość wznoszenia", "transmission": "Skrzynia biegów",
           "reloadBase": "Przeładowanie (podstawowe)", "reloadAced": "Przeładowanie (mistrzowskie)", "vertTraverse": "Szybkość celowania w pionie",
           "horizTraverse": "Szybkość celowania w poziomie", "hullFront": "Przód kadłuba", "hullSide": "Bok kadłuba",
           "hullRear": "Tył kadłuba", "turretFront": "Przód wieży", "turretSide": "Bok wieży",
           "turretRear": "Tył wieży", "era": "Pancerz reaktywny (ERA)", "composite": "Pancerz kompozytowy", "fitted": "Zamontowany",
           "none": "Brak", "yes": "Tak", "no": "Nie", "radarRange": "Zasięg radaru", "thermal": "Termowizja",
           "genN": "Gen. {n}", "rwr": "Odbiornik ostrzegawczy radaru (RWR)", "laserWarning": "Ostrzeżenie laserowe",
           "ballisticComputer": "Komputer balistyczny"},
    language={"label": "Język", "translateToggle": "Przetłumacz dane pojazdu", "translating": "Tłumaczenie…",
              "translateError": "Tłumaczenie niedostępne — wyświetlono tekst oryginalny.",
              "needsApiKey": "Nie skonfigurowano klucza API tłumaczenia."},
)


def validate_key_parity():
    """Every locale must have exactly the same keys as English — a missing
    key silently falls back to showing the key name in the UI, which is a
    worse failure mode than an English fallback would be."""
    def flatten(d, prefix=""):
        keys = set()
        for k, v in d.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys |= flatten(v, path)
            else:
                keys.add(path)
        return keys

    en_keys = flatten(MESSAGES["en"])
    problems = []
    for locale, data in MESSAGES.items():
        if locale == "en":
            continue
        keys = flatten(data)
        missing = en_keys - keys
        extra = keys - en_keys
        if missing:
            problems.append(f"{locale}: missing {sorted(missing)}")
        if extra:
            problems.append(f"{locale}: extra {sorted(extra)}")
    if problems:
        raise SystemExit("Key parity check failed:\n" + "\n".join(problems))
    print(f"Key parity OK — {len(en_keys)} keys x {len(MESSAGES)} locales.")


def main():
    validate_key_parity()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for locale, data in MESSAGES.items():
        path = OUT_DIR / f"{locale}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  {locale}.json  ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
