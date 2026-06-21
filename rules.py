# -*- coding: utf-8 -*-
"""Rule-based keywords and heuristics for Tech Radar classification."""
from __future__ import annotations

import re
from typing import Iterable

QUADRANT_LABELS: list[str] = [
    "Технологии искусственного интеллекта",
    "Технологии цифровых двойников",
    "Технологии машинного зрения",
    "Технологии IoT и интернет вещей",
    "Технологии роботизации и полифункциональных роботов",
    "Технологии квантовых коммуникаций и гибридные квантовые вычисления",
    "Технологии блокчейн",
    "Технологии энергоэффективности и устойчивого развития",
    "Технологии импортозамещения и реновация",
    "Технологии новых материалов и химическая технология",
    "Технологии новых решений на основе палладия",
    "Технологии интеллектуальных систем управления производством",
    "Технологии промышленной автоматизации",
    "Технологии системы логистики",
    "Технологии кибербезопасности",
    "Технологии интеграционных решений и хранения данных",
    "Технологии AR\\VR для металлургии",
    "Технологии на основе больших языковых моделей",
    "Технологии систем на базе LLM RAG",
    "Технологии систем на базе агентной LLM",
    "Батарейные технологии",
    "Аддитивные технологии (3D-печать)",
    "Промышленная безопасность (цифровая)",
    "Биотехнологии",
]

BLOCK_LABELS: list[str] = [
    "Блок СВП-Операционный директор",
    "Блок корпоративных, акционерных и правовых вопросов",
    "Блок Аппарата",
    "Взаимодействие с организациями и органами власти",
    "Блок кадровой, социальной политики и связей с общественностью",
    "Блок стратегии и развития бизнеса",
    "Блок СВП - Производственный директор",
    "Блок энергетики",
    "Блок по корпоративной и экономической безопасности",
    "Блок экономики и финансов",
    "Блок сбыта, коммерции и логистики",
    "Блок внутреннего контроля и риск-менеджмента",
    "Блок рисков, контролей и внутреннего аудита",
    'Блок Президента ГО ПАО "ГМК НН" Безопасность. Мобилизационная подготовка',
    "Блок безопасность. Специальная документальная связь",
    "Блок капитального строительства",
]

# Dataset typo alias used in source.xlsx labels.
QUADRANT_ALIASES: dict[str, str] = {
    "Технологии на основе больших яхыковых моделей": (
        "Технологии на основе больших языковых моделей"
    ),
}

NN_SPUTNIK_PATTERNS: list[str] = [
    "НН-Спутник",
    "нн-спутник",
    "NN-Sputnik",
    "Вне КПМ",
]

BLOCK_ALIASES: dict[str, str] = {
    "Блок рисков,контролей и внутреннего аудита": "Блок рисков, контролей и внутреннего аудита",
    "Корпоративный центр": "Блок Аппарата",
    "\u200bБлок СВП-Операционный директор": "Блок СВП-Операционный директор",
    "\u200bБлок сбыта, коммерции и логистики": "Блок сбыта, коммерции и логистики",
    "\u200bБлок стратегии и развития бизнеса": "Блок стратегии и развития бизнеса",
    "\u200bБлок экономики и финансов": "Блок экономики и финансов",
}

NAME_WEIGHT = 0.55
DESC_WEIGHT = 0.45
RULE_ENSEMBLE_WEIGHT = 0.4
SEMANTIC_ENSEMBLE_WEIGHT = 0.6
LOW_CONFIDENCE_THRESHOLD = 0.6

QUADRANT_KEYWORDS: dict[str, list[str]] = {
    "Технологии искусственного интеллекта": [
        "нейросет", "машинное обучение", "ml", "искусственный интеллект",
        "предиктивн", "когнитивн", "глубокое обучение", "классификац",
        "оптимизац", "рекомендательн", "аналитик", "ии-", " ии ",
    ],
    "Технологии на основе больших языковых моделей": [
        "llm", "большая языковая модель", "языковая модель", "яхыковая модель",
        "генеративн", "gpt", "chatgpt", "foundation model", "erudit", "эрудит",
    ],
    "Технологии систем на базе LLM RAG": [
        "rag", "retrieval", "векторн", "embedding", "поиск по документам",
        "база знаний", "semantic search", "metalassistant",
    ],
    "Технологии систем на базе агентной LLM": [
        "агент", "мультиагент", "agent", "autonomous", "автономн агент",
        "llm-агент", "agentic", "ai agent",
    ],
    "Технологии цифровых двойников": [
        "цифровой двойник", "digital twin", "виртуальная модель",
        "имитационное моделирование", "simulation twin",
    ],
    "Технологии IoT и интернет вещей": [
        "iot", "iiot", "датчик", "сенсор", "беспроводн", "мониторинг оборудования",
        "интернет вещей", "телеметр", "lorawan", "mqtt",
    ],
    "Технологии машинного зрения": [
        "компьютерное зрение", "машинное зрение", "видеоаналитик", "оптическ",
        "камер", "распознавани", "opencv", "дефект",
    ],
    "Технологии роботизации и полифункциональных роботов": [
        "робот", "кобот", "cobot", "манипулятор", "дрон", "бпла", "agv",
    ],
    "Технологии блокчейн": [
        "блокчейн", "blockchain", "смарт-контракт", "smart contract",
        "децентрализованн", "токен", "nft", "distributed ledger",
        "hyperledger", "ethereum", "цифровой актив", "программируем договор",
        "закупок мтр", "реестр транзак", "consensus", "hash", "криптограф",
        "web3", "dlt", "notarization", "децентрализованный реестр",
        "реестр сертификат", "блокчейн-систем",
    ],
    "Технологии квантовых коммуникаций и гибридные квантовые вычисления": [
        "квантов", "quantum", "квантовое шифрование", "квантовый сенсор",
        "qkd", "квантовый комп", "кубит", "qubit", "post-quantum",
        "квантовая связ", "квантовый ключ", "квантовая крипт", "ionq",
        "квантовый генератор", "квантовая случайност", "квантовая памят",
        "гибридн квант", "quantum-safe", "pqc", "квантовое моделирование",
        "квантовая оптимизация", "квантовые сенсоры", "квантовой механики",
    ],
    "Технологии промышленной автоматизации": [
        "плк", "plc", "scada", "автоматизированн систем", "асу", "асутп",
        "контроллер", "автоматическ контрол", "sinamics", "siemens",
        "minemanager", "minepro", "micromine", "minesched", "deswik",
        "горнодобыв", "рудник", "шахт", "карьер",
    ],
    "Технологии интеллектуальных систем управления производством": [
        "mes", "dcs", "управление производством", "диспетчерск",
        "мультиагентная система управлени", "asutp", "erp", "eams",
    ],
    "Технологии кибербезопасности": [
        "кибербезопасност", "сертификат", "шифровани", "защита данных",
        "мониторинг безопасности", "siem", "dlp", "soc", "firewall",
    ],
    "Технологии энергоэффективности и устойчивого развития": [
        "энергоэффективност", "рекуперац", "выброс", "устойчивое развитие",
        "углеродн", "co2", "esg", "carbon",
    ],
    "Технологии AR\\VR для металлургии": [
        " ar ", " vr ", "дополненная реальность", "виртуальная реальность",
        "тренажер", "симулятор", "vr-тренаж", "metaverse", "hololens",
        "oculus", "unity3d", "unreal engine", "сталевар", "металлург",
        "электролит", "immersive", "3d-визуал", "ar-очк", "vr-очк",
        "mixed reality", "mr ", "virtual training",
    ],
    "Технологии системы логистики": [
        "логистик", "маршрут", "склад", "поставк", "tms", "wms", "грузопоток",
        "supply chain", "запас",
    ],
    "Батарейные технологии": [
        "батарея", "аккумулятор", "электролит", "топливный элемент",
        "накопитель энергии", "литий-ион", "li-ion", "суперконденсатор",
        "энергоаккумулятор", "battery", "fuel cell", "cathode", "anode",
        "электрохим", "накопител", "BESS", "flow battery",
    ],
    "Аддитивные технологии (3D-печать)": [
        "3d-печать", "3d печат", "аддитивн", "послойн", "прототипирование деталей",
    ],
    "Промышленная безопасность (цифровая)": [
        "промышленная безопасность", "сиз", "средства защиты", "опасная зона",
        "инцидент", "травм", "safety",
    ],
    "Технологии новых материалов и химическая технология": [
        "материал", "сплав", "огнеупор", "флюс", "химическ", "покрытие",
        "коррозия", "футеровк", "шихт", "флотац",
    ],
    "Технологии интеграционных решений и хранения данных": [
        "интеграция", "esb", "шина данных", "хранилище", "etl", "datalake",
        "kafka", "api gateway",
        # СЭД / ECM
        "электронный документооборот", "сэд", "ecm", "docsvision", "directum",
        "тезис", "дело", "landocs", "docs vision", "документооборот",
        "согласование документов", "маршрутизация документов", "архив документов",
        "контент-менеджмент", "компанимедиа", "elma", "bpm",
        # BI / аналитика
        "bi платформ", "business intelligence", "аналитическая платформ",
        "plandesigner", "optimacros", "olap", "tableau", "qlik", "power bi",
        "бюджетирование платформ", "финансовое планирование платформ",
        # СУБД / инфраструктура данных
        "субд", "postgres", "postgresql", "oracle db", "ms sql", "база данных",
        "хранилище данных", "dwh", "data warehouse", "arenadata",
    ],
    "Технологии импортозамещения и реновация": [
        "импортозамещ", "реновац", "отечествен", "российск", "реестр po",
        "core it", "перевооружен",
    ],
    "Технологии новых решений на основе палладия": [
        "паллад", "palladium", "pd-покрыт", "катализ", "pd-coating",
        "палладиев", "platinum group", "pgm", "кatalizator palladium",
        "платino", "платинов", "каталитическ", "гидrogenation",
        "selective hydrogenation", "pd-слой", "палладий-содержа",
        "precious metal", "благородн металл", "pd-катализ", "аммиак",
        "метан", "каталитическ систем",
    ],
    "Биотехнологии": [
        "биотех", "микробиolog", "фермент", "геном", "bioengineering",
        "biotech", "microorganism", "bacteria", "yeast", "bioleaching",
        "биовыщелач", "biooxidation", "biox", "metagenom", "dna",
        "синbio", "fermentation", "штамм", "культура микроорганизм",
        "biohydrometallurgy", "bio-remediation",
    ],
}

BLOCK_KEYWORDS: dict[str, list[str]] = {
    "Блок СВП - Производственный директор": [
        "производств", "цех", "плавк", "прокатк", "шихт", "металлург", "руда",
        "горнодобыв", "обогащ", "фабрик", "печ", "футеровк", "asutp", "mes",
        "scada", "оператор цех",
        "карьер", "шахт", "горное", "буровой", "взрывн", "вскрыш",
        "рудник", "добыч", "minemanager", "micromine", "minesched", "deswik",
        "minepro", "pit", "маркшейдер", "концентрат", "хвосты обогащени",
        "конвертер", "агломерац", "окатыш", "кокс", "агрегат",
    ],
    "Блок СВП-Операционный директор": [
        "операцион", "устойчивое развитие", "sd.", "развитие территор",
        "членство в ассоциац",
    ],
    "Блок энергетики": [
        "энергетик", "электроснабжени", "трансформатор", "нагревательн",
        "топлив", "водород", "eg.", "подстан",
    ],
    "Блок экономики и финансов": [
        "финанс", "налог", "ндс", "бухгалтер", "бюджет", "экономик", "fm.",
        "erp", "sap", "ifrs", "мсфо", "казнач",
        "бюджетирование", "планирование бюджет", "финансовая модел",
        "управленческий учёт", "казначейств", "plandesigner", "optimacros",
        "финансовая отчётност", "рсбу", "bi финанс",
    ],
    "Блок сбыта, коммерции и логистики": [
        "сбыт", "продажи", "клиент", "логистика", "поставк", "склад", "закупк",
        "маршрут", "sm.", "scm.", "tms", "wms", "закупок мтр",
    ],
    "Блок внутреннего контроля и риск-менеджмента": [
        "контрол", "риск", "инспекция", "мониторинг нарушени", "комплаенс",
        "grc", "rm.", "смарт-контракт", "закупок",
    ],
    "Блок рисков, контролей и внутреннего аудита": [
        "аудит", "ia.", "внутренний аудит", "контрол качеств", "дефект",
    ],
    "Блок кадровой, социальной политики и связей с общественностью": [
        "кадр", "персонал", "обучени", "сотрудник", "социальн", "hr", "hr.",
        "lms", "рекрут",
    ],
    "Блок корпоративных, акционерных и правовых вопросов": [
        "договор", "контракт", "юридическ", "правов", "акционер", "регулятор",
        "cg.", "ls.", "com.",
        "договорн", "контрактн", "претензионн",
        "корпоративн управлени", "акционерн", "доверенност",
        "нотариальн", "судебн", "compliance",
    ],
    "Блок капитального строительства": [
        "строительств", "подрядчик", "смр", "проект строительства", "капитальн",
        "bim",
    ],
    "Блок Аппарата": [
        "документооборот", "архив", "регламент", "ds.", "перевод",
        "технической документац", "делопроизвод",
        "электронный документооборот", "сэд", "ecm", "согласование",
        "входящая корреспонденц", "исходящая корреспонденц", "приказ",
        "распоряжени", "поручени", "нормативные документы",
        "архив документов", "канцеляри",
        "directum", "docsvision", "тезис", "landocs", "elma",
    ],
    "Блок стратегии и развития бизнеса": [
        "стратег", "roadmap", "портфел", "цифровая трансформац", "stm.",
        "развитие бизнес", "корпоративн", "горизонтальн", "ea tool", "инициатив",
        "цифровой портфел", "it-портфел",
        "postgres", "postgresql", "субд", "база данных", "arenadata",
    ],
    "Блок по корпоративной и экономической безопасности": [
        "экономической безопасност", "объектовая безопасност", "sft.",
        "охрана", "пропуск",
    ],
    "Взаимодействие с организациями и органами власти": [
        "органами власти", "госорган", "регулятор", "gr ", "lobby",
        "взаимодействие с организац",
    ],
    'Блок Президента ГО ПАО "ГМК НН" Безопасность. Мобилизационная подготовка': [
        "мобилизац", "mt.", "gs.", "гражданская оборон",
    ],
    "Блок безопасность. Специальная документальная связь": [
        "специальная документальная связь", "sdc.", "коммерческая тайна", "cs.",
    ],
}

# High-priority regex rules (checked on name first, then full text).
QUADRANT_PRIORITY_RULES: list[tuple[str, str, float]] = [
    (r"\b(llm|gpt|эрудит|erudit|больш\w* языков\w* модел)\b", "Технологии на основе больших языковых моделей", 0.95),
    (r"\b(rag\b|retrieval[\s\-]augment|векторн\w* баз)", "Технологии систем на базе LLM RAG", 0.94),
    (r"(llm[\s\-]агент|агентн\w* llm|agentic|ai agent)", "Технологии систем на базе агентной LLM", 0.94),
    (r"(смарт[\s\-]контракт|smart contract|blockchain|блокчейн|децентрализованн\w* реестр)", "Технологии блокчейн", 0.94),
    (r"(квантов|quantum|qkd|qubit|кубит)", "Технологии квантовых коммуникаций и гибридные квантовые вычисления", 0.94),
    (r"(pd[\s\-]катализ|палладиев|palladium|pgm\b)", "Технологии новых решений на основе палладия", 0.93),
    (r"(bioleaching|биовыщелач|biox\b|biooxidation|bio-remediation)", "Биотехнологии", 0.92),
    (r"(топливн\w* элемент|li[\s\-]ion|литий[\s\-]ион|bess\b)", "Батарейные технологии", 0.91),
    (r"(vr[\s\-]тренаж|ar[\s\-]очк|hololens|immersive training)", "Технологии AR\\VR для металлургии", 0.90),
    (r"(цифров\w* двойник|digital twin)", "Технологии цифровых двойников", 0.92),
    (r"(\biot\b|iiot|беспроводн\w* датчик|датчик\w* температур|беспроводн\w* мониторинг)", "Технологии IoT и интернет вещей", 0.93),
    (r"(scada|mes\b|dcs\b|асутп|асу\s*тп)", "Технологии интеллектуальных систем управления производством", 0.90),
    (r"(plandesigner|optimacros|olap\b|bi платформ)", "Технологии интеграционных решений и хранения данных", 0.88),
    (r"(minemanager|minepro|micromine|minesched|deswik)", "Технологии промышленной автоматизации", 0.88),
    (r"(компьютерн\w* зрен|машинн\w* зрен|видеоаналитик)", "Технологии машинного зрения", 0.89),
    (r"(перевод\b.{0,60}(?:документ|техническ)|ии[\s\-]перевод)", "Технологии искусственного интеллекта", 0.88),
    (r"(агент\b(?!н\w* llm)|мультиагент)(?!.*\bllm\b)", "Технологии искусственного интеллекта", 0.86),
]

BLOCK_PRIORITY_RULES: list[tuple[str, str, float]] = [
    (r"(перевод\b.{0,80}документ|технической документац|ds\.)", "Блок Аппарата", 0.92),
    (r"(erudit|эрудит|умн\w* поиск.{0,60}(?:llm|языков\w* модел))", "Блок СВП - Производственный директор", 0.87),
    (r"(смарт[\s\-]контракт|закупок мтр|материально[\s\-]техническ)", "Блок внутреннего контроля и риск-менеджмента", 0.90),
    (r"(футеровк|печ|металлург|цех|плавк|обогащ)", "Блок СВП - Производственный директор", 0.88),
    (r"(sap\b|erp\b|ндс|бухгалтер|финанс)", "Блок экономики и финансов", 0.86),
    (r"(сиз|промышленн\w* безопасност|опасная зона|травм)", "Блок СВП - Производственный директор", 0.85),
    (r"(аудит\b|внутренн\w* аудит|ia\.)", "Блок рисков, контролей и внутреннего аудита", 0.84),
    (r"(minemanager|minepro|micromine|minesched|deswik|горнодобыв|рудник|шахт|карьер)", "Блок СВП - Производственный директор", 0.88),
    (r"(directum|docsvision|сэд\b|ecm\b|электронн\w* документооборот)", "Блок Аппарата", 0.88),
    (r"(plandesigner|optimacros|бюджетирован|финансов\w* план)", "Блок экономики и финансов", 0.88),
    (r"(postgres|postgresql|arenadata|субд\b)", "Блок стратегии и развития бизнеса", 0.72),
]

DISAMBIGUATION_RULES: list[dict] = [
    {
        "name": "СЭД_ECM_to_integration",
        "trigger_keywords": [
            "электронный документооборот", "сэд", "ecm", "docsvision",
            "directum", "тезис", "документооборот", "согласование документов",
        ],
        "condition": "any",
        "veto_rings": ["Перспективные Российские технологии"],
        "target_quadrant": "Технологии интеграционных решений и хранения данных",
        "overrides": [
            "Технологии импортозамещения и реновация",
            "Технологии искусственного интеллекта",
        ],
        "min_confidence_to_apply": 0.0,
    },
    {
        "name": "BI_planning_to_integration",
        "trigger_keywords": [
            "bi платформ", "business intelligence", "olap", "plandesigner",
            "optimacros", "аналитическая платформ", "бюджетирование платформ",
            "финансовое планирование платформ", "дашборд", "отчётност",
        ],
        "condition": "any",
        "veto_rings": [],
        "target_quadrant": "Технологии интеграционных решений и хранения данных",
        "overrides": [
            "Технологии искусственного интеллекта",
            "Технологии импортозамещения и реновация",
        ],
        "min_confidence_to_apply": 0.0,
    },
    {
        "name": "mining_to_prom_automation",
        "trigger_keywords": [
            "minemanager", "minepro", "micromine", "minesched", "deswik",
            "горнодобыв", "рудник", "шахт", "карьер", "горное по",
        ],
        "condition": "any",
        "veto_rings": [],
        "target_quadrant": "Технологии промышленной автоматизации",
        "overrides": [
            "Технологии импортозамещения и реновация",
            "Технологии интеллектуальных систем управления производством",
        ],
        "min_confidence_to_apply": 0.0,
    },
]

PRODUCTION_BLOCK_FALLBACK = "Блок СВП - Производственный директор"
DEFAULT_QUADRANT = "Технологии импортозамещения и реновация"
DEFAULT_BLOCK = "Блок стратегии и развития бизнеса"


def normalize_text(text: object) -> str:
    s = str(text or "").lower().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def canonical_quadrant(label: object) -> str | None:
    if label is None or (isinstance(label, float) and str(label) == "nan"):
        return None
    raw = str(label).strip().replace("\u200b", "")
    if not raw:
        return None
    mapped = QUADRANT_ALIASES.get(raw, raw)
    return mapped if mapped in QUADRANT_LABELS else None


def is_nn_sputnik_block(value: object) -> bool:
    text = str(value or "").replace("\u200b", "")
    if not text or text.lower() == "nan":
        return False
    return any(pattern in text for pattern in NN_SPUTNIK_PATTERNS)


def normalize_block(raw_block: object, use_semantic: bool = True) -> str | None:
    if raw_block is None or (isinstance(raw_block, float) and str(raw_block) == "nan"):
        return None
    raw = str(raw_block).strip().replace("\u200b", "")
    if not raw or is_nn_sputnik_block(raw):
        return None
    if raw in BLOCK_LABELS:
        return raw
    if raw in BLOCK_ALIASES:
        return BLOCK_ALIASES[raw]
    if not use_semantic:
        return None
    return _nearest_block_label(raw)


def _nearest_block_label(raw: str) -> str:
    from difflib import SequenceMatcher

    best_label = DEFAULT_BLOCK
    best_score = 0.0
    candidates = list(BLOCK_LABELS) + list(BLOCK_ALIASES.keys())
    raw_norm = normalize_text(raw)
    for candidate in candidates:
        score = SequenceMatcher(None, raw_norm, normalize_text(candidate)).ratio()
        if score > best_score:
            best_score = score
            best_label = BLOCK_ALIASES.get(candidate, candidate)
    return best_label if best_score >= 0.72 else DEFAULT_BLOCK


def canonical_block(label: object) -> str | None:
    if is_nn_sputnik_block(label):
        return None
    return normalize_block(label, use_semantic=True)


def build_weighted_text(name: str, description: str) -> tuple[str, str, str]:
    name_n = normalize_text(name)
    desc_n = normalize_text(description)
    full = f"{name_n} | {desc_n}".strip(" |")
    return name_n, desc_n, full


def _keyword_hits(text: str, keywords: Iterable[str]) -> int:
    hits = 0
    padded = f" {text} "
    for kw in keywords:
        token = kw.strip().lower()
        if not token:
            continue
        if token.startswith("\\b") or "|" in token or "(" in token:
            if re.search(token, text, flags=re.I):
                hits += 1
        elif token in padded or token in text:
            hits += 1
    return hits


def score_labels(
    name: str,
    description: str,
    keyword_map: dict[str, list[str]],
    labels: list[str],
    priority_rules: list[tuple[str, str, float]] | None = None,
) -> dict[str, float]:
    name_n, desc_n, full = build_weighted_text(name, description)
    scores = {label: 0.0 for label in labels}

    if priority_rules:
        for pattern, label, weight in priority_rules:
            if label not in scores:
                continue
            if re.search(pattern, name_n, flags=re.I):
                scores[label] = max(scores[label], weight * 1.05)
            elif re.search(pattern, full, flags=re.I):
                scores[label] = max(scores[label], weight)

    for label, keywords in keyword_map.items():
        if label not in scores:
            continue
        name_hits = _keyword_hits(name_n, keywords)
        desc_hits = _keyword_hits(desc_n, keywords)
        if name_hits or desc_hits:
            raw = NAME_WEIGHT * name_hits + DESC_WEIGHT * desc_hits
            scores[label] = max(scores[label], min(0.98, 0.35 + raw * 0.12))

    # Quadrant-specific disambiguation heuristics.
    if keyword_map is QUADRANT_KEYWORDS:
        if re.search(r"\b(llm|gpt|языков\w* модел|яхыков\w* модел)\b", full, flags=re.I):
            scores["Технологии искусственного интеллекта"] *= 0.55
            for llm_label in (
                "Технологии на основе больших языковых моделей",
                "Технологии систем на базе LLM RAG",
                "Технологии систем на базе агентной LLM",
            ):
                if scores.get(llm_label, 0) > 0:
                    scores[llm_label] *= 1.15

        if re.search(r"\b(mes|scada|dcs|асутп)\b", full, flags=re.I):
            scores["Технологии интеллектуальных систем управления производством"] *= 1.2
            scores["Технологии искусственного интеллекта"] *= 0.85

        if "виртуальн" in full and "датчик" in full:
            scores["Технологии IoT и интернет вещей"] *= 1.15
            if not re.search(r"\b(ml|машинн\w* обуч|нейросет)\b", full, flags=re.I):
                scores["Технологии искусственного интеллекта"] *= 0.8

        if re.search(r"(беспроводн|датчик|сенсор|iot|iiot)", full, flags=re.I) and re.search(
            r"(футеровк|огнеупор|материал)", full, flags=re.I
        ):
            scores["Технологии IoT и интернет вещей"] *= 1.35
            scores["Технологии новых материалов и химическая технология"] *= 0.45

    return scores


def normalize_ring(ring: object) -> str:
    raw = str(ring or "").strip()
    if not raw or raw.lower() == "nan":
        return ""
    if "Перспективные Российские" in raw:
        return "Перспективные Российские технологии"
    if "Перспективные Мировые" in raw:
        return "Перспективные Мировые технологии"
    if raw.startswith("Прототипируется") or "прототипирован" in raw.lower():
        return "Прототипируется"
    return raw


def _rule_triggered(text: str, keywords: list[str], condition: str = "any") -> bool:
    hits = [_keyword_hits(text, [kw]) > 0 for kw in keywords]
    if condition == "all":
        return bool(hits) and all(hits)
    return any(hits)


def apply_quadrant_disambiguation(
    text: str,
    ring: str | None,
    scores: dict[str, float],
) -> dict[str, float]:
    adjusted = scores.copy()
    norm_ring = normalize_ring(ring)

    for rule in DISAMBIGUATION_RULES:
        veto_rings = rule.get("veto_rings", [])
        if norm_ring and norm_ring in veto_rings:
            continue
        if not _rule_triggered(text, rule.get("trigger_keywords", []), rule.get("condition", "any")):
            continue

        current_top = max(adjusted, key=lambda k: adjusted[k]) if adjusted else ""
        current_conf = adjusted.get(current_top, 0.0)
        if current_conf < rule.get("min_confidence_to_apply", 0.0):
            continue

        target = rule["target_quadrant"]
        adjusted[target] = max(adjusted.get(target, 0.0), 0.85)
        for override in rule.get("overrides", []):
            if override in adjusted:
                adjusted[override] *= 0.45

    return adjusted


def scores_to_ranking(scores: dict[str, float], top_k: int = 3) -> list[tuple[str, float]]:
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    if not ranked or ranked[0][1] <= 0:
        return []
    top_score = ranked[0][1]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = max(0.0, top_score - second_score)
    scale = min(1.0, top_score + margin * 0.5)
    return [
        (label, round(min(1.0, value / top_score * scale), 4))
        for label, value in ranked[:top_k]
        if value > 0
    ]


def apply_process_code_boost(text: str, scores: dict[str, float], process_codes: dict[str, list[str]]) -> None:
    for block, codes in process_codes.items():
        if block not in scores:
            continue
        for code in codes:
            if code.lower() in text:
                scores[block] = max(scores[block], scores.get(block, 0) + 0.25)


def disambiguate_blocks(name: str, description: str, scores: dict[str, float]) -> dict[str, float]:
    _, _, full = build_weighted_text(name, description)
    prod_score = scores.get(PRODUCTION_BLOCK_FALLBACK, 0)
    if prod_score > 0.45 and not any(
        scores.get(label, 0) >= prod_score
        for label in scores
        if label != PRODUCTION_BLOCK_FALLBACK
    ):
        scores[PRODUCTION_BLOCK_FALLBACK] = min(prod_score, 0.72)

    if re.search(r"(сиз|промышленн\w* безопасност|опасная зона|травм)", full, flags=re.I):
        scores["Блок внутреннего контроля и риск-менеджмента"] *= 0.7
        scores[PRODUCTION_BLOCK_FALLBACK] = max(
            scores.get(PRODUCTION_BLOCK_FALLBACK, 0), 0.55
        )

    if re.search(r"(аудит|контрол качеств|дефект\b|grc\b)", full, flags=re.I):
        scores["Блок внутреннего контроля и риск-менеджмента"] *= 1.15
        scores["Блок рисков, контролей и внутреннего аудита"] *= 1.1

    return scores
