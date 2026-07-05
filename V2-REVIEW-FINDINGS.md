# Ревью кита — находки и план правок для v2.0

> Дата ревью: 2026-07-04 | Ревью версии: 1.6.2 (текущая после точечных правок: 1.6.3)
>
> **Принятые решения:**
> - Выпускаем **v2.0 без обратной совместимости** — ломающие правки допустимы, миграция существующих vault'ов не требуется.
> - **Obsidian остаётся обязательной частью** (Dataview / Metadata Menu / Bases) — требования читают и люди; дашборды чинить, а не выбрасывать.

---

## Уже исправлено (v1.6.3, 2026-07-04)

- ✅ **REQUIREMENTS-OVERVIEW, запрос 7a** — фильтровал по `verified_by` во frontmatter, которого после link-up-only (v0.5.0) там нет → показывал все FR/NFR как непокрытые. Переписан: обратные ссылки вычисляются на лету из `verifies` в TEST-артефактах.
- ✅ **REQUIREMENTS-OVERVIEW, запрос 7d (новый)** — FR без доставляющей US: `delivered_by` вычисляется из `delivers` в US.
- ✅ В секцию 7 добавлена заметка: обратные ссылки всегда вычисляются, никогда не хранятся.
- ✅ CHANGELOG + версия в README обновлены.

---

## П.1 — Висячие ссылки на удалённый `_framework/status-transitions.md` 🔴 критично ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** файл снова генерируется из `kit-manifest.json` скриптом `generate-status-transitions.py`; все ссылки резолвятся. `grep status-transitions` по `.md`/`.py` чист (остались только валидные ссылки на существующий файл и на `check-status-transitions.py`).

Файл удалён в v1.6.0 (см. CHANGELOG), но на него по-прежнему ссылаются:

- `README.md` — строка «Status transition rules (state machines)... (`_framework/status-transitions.md`)» и принцип №6 «Status transitions are enforced. See ...»
- `docs/agent-instructions.md` — раздел «Status Transitions»: «See `{{VAULT_PREFIX}}/_framework/status-transitions.md`... Do not skip states.» (и все сгенерированные агент-файлы после установки)
- `_framework/sdlc-pipeline.md` — принцип №3 «No stage skipping... (see `status-transitions.md`)»
- `scripts/README-FIRST.md` — шаг 4 «Review `_framework/status-transitions.md`»
- `scripts/agent-prompts.md` — промпт Librarian: «see `_framework/status-transitions.md`»

**Почему важно:** агент, следуя инструкции, упирается в несуществующий файл. Для AI-first документации ссылочная целостность обязана быть проверяемой.

**Правка:** удалить/заменить все ссылки. Куда указывать вместо файла — см. п.6 (либо на JSON-схемы как источник допустимых статусов, либо на новый раздел в манифесте). После правки прогнать grep `status-transitions` по всем `.md`/`.py`. Рассмотреть CI-проверку целостности внутренних ссылок в доках кита.

---

## П.2 — Пример FR-INGEST-001 нарушает правила самого кита 🔴 критично ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** FR-INGEST-001 переписан (атомарный, link-up-only, без полей вне схемы); вычищены NFR-SEC-001, US-INGEST-001, TASK-INGEST-001, ADR-INGEST-001, CON-SEC-001, PRODUCT-VISION. Добавлена полная цепочка `SRC-COMPLY-001 → BRQ-COMPLY-001 → BR-COMPLY-001 → FR-INGEST-001` и ветка безопасности `BRQ-SEC-001 → CTRL-SEC-001 → NFR-SEC-001`. Все примеры проходят `validate-frontmatter`, `check-duplicates`, `check-orphans`, `check-status-transitions`.

`_examples/02-requirements/fr/FR-INGEST-001.md`:

1. **Обратные ссылки во frontmatter** — `delivered_by`, `implemented_by`, `verified_by` заполнены вручную, вопреки link-up-only («computed automatically — do not add manually»).
2. **Нет `derives_from`** — по правилу кита («Do not create FR/NFR/CON without linking to at least one BRQ») это orphan. В `_examples/` вообще нет BRQ/BR/CTRL-примеров, поэтому цепочка obligation stack не продемонстрирована.
3. **Misuse `source_docs: [[EPIC-INGEST-001]]`** — поле предназначено для внешних документов («Only if derives_from is empty»), а Epic уже есть в `parent_epic`.
4. **Поля вне шаблона и схемы** — `type`, `component`, `stakeholders`, `risk`, `release_target`, `blocks`. Агент видит три конфликтующих образца: шаблон ≠ схема ≠ пример.
5. **Секция Requirement дословно дублирует Summary** и содержит составное требование (принять + аутентифицировать + персистировать) — нарушение атомарности, плохой образец.

**Правка:** привести все `_examples/` в строгое соответствие шаблонам и схемам v2.0; добавить примеры SRC → BRQ → BR → FR, чтобы цепочка была видна целиком. Проверить остальные примеры на те же паттерны (US, EPIC, TASK, TEST, ADR, CR). Примеры — то, что агенты копируют; это самая дешёвая правка с самым высоким эффектом.

---

## П.3 — Дашборд REQUIREMENTS-OVERVIEW ✅ ВЫПОЛНЕНО (v2.0)

Остаточная проверка для v2.0: секция 8 «Assumptions at Risk» использует `related_requirements` — поле помечено как legacy в `generate-traceability.py`. Сверить с актуальным шаблоном ASSUM и схемой; если поле живое для ASSUM — убрать его из legacy-списка, если legacy — переписать запрос.

**Сделано:** `related_requirements` — живое поле (есть в схемах ASSUM/UC/ADR/CONTRACT/DM/JOURNEY/ARCH), поэтому запрос секции 8 корректен. В `generate-traceability.py` `related_requirements` и `related_adrs` перенесены из legacy-группы в живые reference-ссылки.

---

## П.4 — `contracts/` vs `integrations/` 🔴 критично ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** папка переименована `integrations/` → `contracts/`; обновлены README, оба typeMap в `REQUIREMENTS-OVERVIEW.md`, `kit-manifest.json`, перегенерён fileClass CONTRACT. `architecture-overview.md` теперь создаётся из шаблона (README уточнён), плюс добавлен пример в `_examples/`.

- `README.md` (folder layout): `03-architecture/contracts/ # API and interface contracts`
- Фактическая папка: `03-architecture/integrations/` (в README не упомянута вовсе)
- `REQUIREMENTS-OVERVIEW.md`: мапит Contract → `03-architecture/integrations`

**Правка (v2.0, совместимость не нужна):** выбрать одно имя. Рекомендация — `contracts/` (совпадает с типом артефакта CONTRACT и шаблоном contract-template.md), переименовать папку, обновить README и оба typeMap в REQUIREMENTS-OVERVIEW. Заодно: README обещает `architecture-overview.md` в `03-architecture/` — файла нет (есть только шаблон); решить, шипить ли заготовку.

---

## П.5 — Версионный мусор в корне 🟡 ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** `.kit-version` = `2.0.0` (единственный машиночитаемый источник версии, без битой ссылки на скрипт). Удалены `.kit-version.test`, `_temp/`, `migration-report.md`, `.snapshots/`. В `.gitignore` добавлены `_temp/`, `*.test`, `.snapshots/`.

- `.kit-version` = `1.3.0` при README 1.6.x; ссылается на несуществующий `scripts/preprocessor/promote.py`
- `.kit-version.test` — тестовый leftover
- `_temp/` — пустая папка
- `migration-report.md` — отчёт dry-run от 2026-03-31
- `.snapshots/` — данные Obsidian-плагина (config.json, readme.md, sponsors.md)

**Правка:** `.kit-version` сделать единственным машиночитаемым источником версии (README её отображает) и чинить механизм обновления; остальное удалить и добавить в `.gitignore` (`_temp/`, `.snapshots/`, `*.test`). Корень репозитория — сигнал для агента, мусор = шум в контексте.

---

## П.6 — «Status transitions are enforced» — преувеличение 🟡 ✅ ВЫПОЛНЕНО (v2.0, вариант 1)

**Сделано:** реализована честная проверка переходов — `check-status-transitions.py --git [--git-base REF]` берёт старый статус из git, новый из рабочего дерева и сверяет с графом переходов из `kit-manifest.json` (draft→approved минуя proposed отклоняется; проверено). Принцип №6 README переформулирован. Граф и `status-transitions.md` генерируются из манифеста.

`check-status-transitions.py` проверяет только: (а) валидность текущего статуса по enum, (б) согласованность parent/child. **Переходы** (draft→approved минуя proposed) не проверяются — для этого нужна git-история.

**Правка (одно из двух):**
1. Реализовать честную проверку переходов в CI: сравнение старого/нового значения `status` по `git diff` против графа разрешённых переходов (граф — в манифест, см. п.7).
2. Либо переформулировать принцип №6 README и удалить обещание state machines.

Рекомендация — вариант 1: автономным агентам нужен именно машинный gate, а не соглашение.

---

## П.7 — Единый машиночитаемый манифест кита 🟠 системное, ломающее ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** создан `kit-manifest.json` (для каждого типа: префикс, папка, схема, tier, lifecycle-флаг, статусы, граф переходов, up-link-поля с типами целей) + загрузчик `scripts/kit_manifest.py`. Из манифеста теперь читают `validate-frontmatter.py` (prefix→schema), `check-status-transitions.py` (статусы + граф), `generate-fileclasses.py` (папки, иконки), `generate-status-transitions.py`, `assemble-context.py`. Хардкод-реестры удалены — источник дрейфа устранён.

Реестр типов артефактов сейчас захардкожен минимум в 5 местах:

- `scripts/validate-frontmatter.py` → `PREFIX_SCHEMA_MAP`
- `scripts/check-status-transitions.py` → `VALID_STATUSES`
- `REQUIREMENTS-OVERVIEW.md` → два typeMap (секции 1 и 4)
- `README.md` → folder layout + tier-модель
- `_metadata-menu/fileclasses/` (генерируются, но из схем, а не из общего реестра)

Дрейф уже случился (п.1, п.4).

**Правка:** создать `kit-manifest.json`: для каждого типа — префикс ID, папка, схема, tier, допустимые статусы, граф переходов, link-поля (up-links) с типами целей. Из манифеста генерировать: константы скриптов, fileclasses, таблицы в README, typeMap для dataview (или блок данных, который запросы читают). Тот же паттерн, что уже применён к агент-файлам (canonical source + generator).

---

## П.8 — Стоимость сборки контекста для агента 🟠 ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** (1) `scripts/assemble-context.py TASK-XXX-NNN` собирает всю trace-цепочку (задача, FR/NFR, US+AC, obligation chain, связанные ADR, target_files) в один markdown-бандл. (2) Ритуал в `agent-instructions.md` тиринговый: обязательные шаги vs условные (compliance/architecture/constraints) с указателем на assemble-context.

Ритуал «Before Starting Any Task» — 8 шагов, 10+ чтений файлов (TASK → FR → US → BRQ/BR/CTRL → SRC → ADR → ARCH → code-map → glossary → constraints). Для тривиальной задачи дорого; агенты будут срезать углы.

**Правка:**
1. Скрипт `assemble-context.py TASK-XXX-NNN` — собирает полную trace-цепочку задачи в один контекст-бандл (markdown): задача, FR, AC из US, выдержки ADR, релевантный срез глоссария, target_files из code-map. Один Read вместо десяти.
2. Тиринг ритуала в agent-instructions: какие шаги обязательны всегда (TASK, FR, US/AC), какие — по условию (SRC/CTRL только для compliance, ARCH только при `estimated_complexity: complex` и т.п.).

---

## П.9 — Дублирование как источник дрейфа 🟠 ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** (1) task-template больше не копирует текст AC — только ссылки AC-N + `acceptance_criteria_subset`. (2) Секция `# Links` удалена из всех шаблонов. (3) Добавлен `scripts/check-updated-dates.py` — warning при расхождении `updated:` с датой последнего git-коммита.

1. **task-template**: «Acceptance Criteria Covered... (copy the criterion here)» — копия текста AC устареет при правке US. → Оставить только ссылки AC-N (`acceptance_criteria_subset` уже есть во frontmatter); текст агент читает из US (или его вставляет assemble-context из п.8).
2. **Секция `# Links` в body** дублирует frontmatter-ссылки (в примере FR присутствуют оба варианта, местами расходятся). → Убрать секцию из шаблонов v2.0 (Obsidian показывает frontmatter-ссылки и backlinks) или генерировать.
3. **`updated:` вручную** — врёт со временем. → Валидировать в CI против git-даты последнего коммита файла (warning при расхождении) или проставлять хуком.

---

## П.10 — Схемы не ловят опечатки в полях 🟠 ломающее ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** во всех схемах `additionalProperties: false` (закрытый набор полей); проектные расширения — по конвенции `x_*`. `validate-frontmatter.py` дополнительно даёт подсказку «did you mean» по расстоянию Левенштейна ≤ 2 (проверено: `derive_from` → предлагает `derives_from`; `x_jira` проходит).

`base.schema.json`: `additionalProperties: true` + все link-поля необязательны → агент пишет `derive_from` вместо `derives_from`, валидация проходит, трассировка молча рвётся. Типовой AI-failure mode.

**Правка (v2.0):** в каждой схеме перечислить допустимые поля явно и `additionalProperties: false`. Для проектных расширений — конвенция `x_*` (разрешить паттерном) или список custom-полей в `project-config.json`. Дешёвая альтернатива-дополнение: проверка в validate-frontmatter «неизвестное поле похоже на известное» (расстояние Левенштейна ≤ 2 → error).

---

## П.11 — Цепочка трассировки смешивает два измерения 🟡 ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** в README (принцип №2) и `agent-instructions.md` нотация разделена на два измерения — obligation chain (`SRC → BRQ → BR/CTRL —(derives_from)→ FR/NFR`) и solution structure (`Epic ⊃ (FR ↔ US) → TASK → TEST`); явно указано, что Epic — группировка, а не звено obligation chain. Link-поля не менялись.

Нотация `[SRC →] BRQ → [BR →] [CTRL →] Epic → FR ↔ US → Task → Test` (README принцип №2, agent-instructions) подразумевает связь «CTRL → Epic», которой семантически нет: Epic — группировка solution space, а не звено obligation chain.

**Правка:** в доках разделить на два измерения:
- Obligation chain: `SRC → BRQ → BR / CTRL —(derives_from)→ FR / NFR`
- Solution structure: `Epic ⊃ (FR ↔ US) → TASK → TEST`

Link-поля не меняются — только нотация и пояснения.

---

## П.12 — Мелочи 🟢 ✅ ВЫПОЛНЕНО (v2.0)

**Сделано:** (1) `docs/success-criteria.md` переведён на английский (0 кириллицы). (2) Папка `05-quality/test-ideas/` удалена; test ideas оформляются как дополнительные TEST-сценарии. (3) Правило резолвинга wiki-links добавлено в `agent-instructions.md`. (4) `_examples/` покрывает все 24 типа. (5) README Quick Start шаг 2 уточнён (CLAUDE.md появляется после `install-agent-files.py`). (6) `estimated_complexity` в agent-prompts соответствует enum в `task.schema.json` — расхождений нет.

1. `docs/success-criteria.md` — на русском при английском ките. Перевести (для единообразия контекста агентов) либо явно пометить как внутренний документ.
2. `05-quality/test-ideas/` — нет ни типа артефакта, ни шаблона, ни схемы. Либо оформить тип (шаблон + схема + манифест), либо удалить папку и оставить test ideas секцией в TEST/US.
3. Правило разрешения wiki-links записать в agent-instructions явно: `[[ID]]` → файл `ID.md`, ID глобально уникален, папка определяется префиксом типа (по манифесту). Важно для не-Obsidian агентов.
4. `_examples/` не покрывает все 24 типа (нет SRC, BRQ, BR, CTRL, JOURNEY, UC, RISK, REL, CONTRACT, DM, NFR-помимо-SEC и др.) — для v2.0 добавить по одному примеру каждого типа, сгенерированных строго из шаблонов.
5. README: Quick Start шаг 2 упоминает `CLAUDE.md` в корне — файл появляется только после `install-agent-files.py`; уточнить формулировку.
6. Проверить `estimated_complexity` в agent-prompts (simple < 50 строк и т.д.) на соответствие enum в task.schema.json.

---

## Порядок работ для v2.0

| Приоритет | Пункты | Характер |
|---|---|---|
| 1 | П.1, П.2, П.4, П.5 | Чинит то, обо что агенты спотыкаются сейчас; не ломающее (кроме переименования папки) |
| 2 | П.7 (манифест) | Фундамент: устраняет класс проблем дрейфа; делать до остальных структурных правок |
| 3 | П.6, П.10 | Машинные gates: честная проверка переходов + строгие схемы (зависят от манифеста) |
| 4 | П.8, П.9 | Экономика контекста агента и устранение дублирования |
| 5 | П.11, П.12 | Документация и гигиена |

После всех правок: bump до **2.0.0**, CHANGELOG с разделом Breaking Changes, прогон всех скриптов на `_examples/` как smoke-test.

---

## ✅ Статус: все пункты выполнены в v2.0.0 (2026-07-04)

Все находки П.1–П.12 закрыты (отметки в каждом разделе выше). Итог:

- Версия поднята до **2.0.0** (`.kit-version`, README), в CHANGELOG добавлен раздел с Breaking Changes.
- Smoke-test на всём репозитории и на `_examples/` зелёный:
  - `validate-frontmatter.py` — ✓ (закрытые схемы + подсказки по опечаткам)
  - `check-duplicates.py` — ✓
  - `check-orphans.py` — ✓
  - `check-status-transitions.py` (snapshot и `--git`) — ✓
  - генераторы `generate-status-transitions.py`, `generate-fileclasses.py`, `generate-traceability*.py`, `assemble-context.py` — ✓
- `_examples/` — единый связный проект DBP, покрывает все 24 типа артефактов.
