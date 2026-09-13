# Artefakt 3 — Kontrybutorzy (kto wie co)

**Repo:** jellyfin (backend serwera, .NET 10)
**Okno:** 2025-09-12 → 2026-09-10
**Wygenerowano:** 2026-09-12
**Wejście:** `artifact-1-territory.md`, `artifact-2-structure.md`

## Metoda i filtry

- `git log --since="12 months ago" --no-merges --author=...` z tym samym filtrem szumu co w artefakcie 1.
- **Odfiltrowane boty:** `renovate[bot]` (164 commity — same bumpy wersji), automatyka Weblate. Tłumacze (`krvi`, `rimasx`, `Vitalijus`, `Lofuuzi`, `Milo Ivir`, `Blackspirits`, `Riccardo`) odpadają automatycznie przy filtrze `*.json` — ich wkład to wyłącznie lokalizacje, nie kod.
- **Commity z współautorstwem AI:** 16 w oknie (`Copilot` 3, `Claude Opus 4.6` 3, reszta bez wyraźnego agenta). Wszystkie mają człowieka jako `author`, AI występuje w trailerze `Co-authored-by`. Zostawione — autorstwo ludzkie jest jednoznaczne.
- **Scalone tożsamości** (ten sam e-mail, dwa zapisy nazwy): `Bond_009` = `Bond-009` (`bond.009@outlook.com`, 34 commity), `Cody Robibero` = `crobibero` (`cody@robibe.ro`, 20 commitów).
- Dane to publiczna historia gita repozytorium open source. Nazwy = handle'e z commitów.

## Top 5 obszarów wymagających kontaktu

Wybrane na przecięciu churnu (artefakt 1) i ryzyka strukturalnego (artefakt 2).

| # | Obszar | Dlaczego trzeba pytać człowieka |
|---|---|---|
| 1 | `MB.Controller/Entities` | fan-in **119**, 22 cykle, churn #3. Zmiana promieniuje najszerzej w repo, a graf nie powie, co się zepsuje |
| 2 | `JSI/Item` (`BaseItemRepository.*`) | churn #1 (279), fan-in **5** — wiązanie przez DI, kompilator nie ostrzeże. 3350 linii w 5 partialach, migracja EF wciąż w toku |
| 3 | `ESI/Library` (`LibraryManager`) | 24 zależności w ctor, 4150 linii, fan-out 52. Nietestowalny jednostkowo, churn #2 wśród plików |
| 4 | `Jellyfin.Server/Migrations` + `JDB` | zmiany nieodwracalne, **zero testów**, sprzężenie `ModelConfiguration`→`Sqlite/Migrations` = 100%. Przed dodaniem PostgreSQL trzeba wiedzieć, co było świadomą decyzją |
| 5 | `MB.Controller/MediaEncoding` + `MB.MediaEncoding` | `EncodingHelper` 8019 linii — największy plik w repo. Nowy front od P3, wiedza domenowa o ffmpeg nie wynika z kodu |

## Linia wsparcia — kto pracował przy czym

### Obszar 1: `MB.Controller/Entities` (model domenowy)

| osoba | commity | aktywność P1→P4 | ostatni commit | tematyka |
|---|---|---|---|---|
| **Shadowghost** | 64 | 7 → 107 → 112 → 170 | 2026-09-07 | model encji, `BaseItem`/`Folder`, powiązanie z repozytorium |
| theguymadmax | 16 | 40 → 25 → 17 → 33 | 2026-09-06 | encje + metadane, `Providers/Manager` |
| dkanada | 4 | 3 → 2 → 12 → 6 | 2026-07-25 | punktowo |
| JPVenson | 4 | 25 → 3 → 8 → **0** | 2026-06-07 | punktowo, od strony migracji |

**Pierwszy kontakt: Shadowghost.** 59% commitów w obszarze.

### Obszar 2: `JSI/Item` — warstwa repozytorium EF Core

| osoba | commity | aktywność | ostatni commit | tematyka |
|---|---|---|---|---|
| **Shadowghost** | 119 | rosnąca | 2026-09-07 | `BaseItemRepository` i wszystkie partiale, `PeopleRepository`, tłumaczenie zapytań |
| theguymadmax | 25 | stabilna | 2026-09-06 | repozytorium + encje + providery — profil generalisty |
| **JPVenson** | 13 | **wygasła** | 2026-06-07 | migracje danych do EF Core — patrz obszar 4 |
| TheMelmacian | 9 | 0 → 0 → 7 → 3 | 2026-07-21 | zapytania i `MB.Model/Querying`, `Controller/Persistence` |
| dkanada | 6 | — | 2026-07-25 | punktowo |

**Pierwszy kontakt: Shadowghost** (57%). **Dla pytań o kontrakt zapytań: TheMelmacian** — jedyna osoba spoza czołówki, która dotykała `Controller/Persistence` i `Model/Querying` razem.

### Obszar 3: `ESI/Library` — `LibraryManager`

| osoba | commity | aktywność | ostatni commit | tematyka |
|---|---|---|---|---|
| **Shadowghost** | 90 | rosnąca | 2026-09-07 | menedżer biblioteki, walidatory, rozwiązywanie elementów |
| theguymadmax | 17 | stabilna | 2026-09-06 | biblioteka + metadane |
| Tim Eisele | 6 | 3 → 1 → 12 → 2 | 2026-08-20 | biblioteka, encje EF, filtry serwera, napisy — profil szeroki, płytki |
| Cody Robibero | — | stała, niska | **2026-09-10** | migracje, filtry, backup, sortowanie — profil „utrzymaniowy" |

**Pierwszy kontakt: Shadowghost** (58%).

### Obszar 4: migracje i baza

| osoba | commity (`Migrations` + `JDB`) | aktywność | ostatni commit | tematyka |
|---|---|---|---|---|
| **Shadowghost** | 51 + 43 | rosnąca | 2026-09-05 | rutyny migracyjne, model EF, migracje SQLite |
| **JPVenson** | 42 + 8 | **12 → 2 → 4 → 0** | **2026-06-07** | **architekt migracji EF Core** — najgłębsza wiedza o wieloproviderowości |
| Cody Robibero | 6 | stała | 2026-09-10 | rutyny, backup |
| Niels van Velzen | 3 | 6 → 3 → 1 → **0** | 2026-06-08 | rutyny + API |

**To najwyższe ryzyko wiedzy w całym repo.** JPVenson ma 341 commitów od 2023 i jest autorem `src/Jellyfin.Database/readme.md` (procedura migracji wieloproviderowej). W P4 zero commitów, ostatni ślad 2026-06-07. Pytania o PostgreSQL, o to dlaczego `Interfaces` ↔ `Entities` jest splątane (cykl 27↔3 z artefaktu 2) i co oznacza `JellyfinMigrationStageTypes` — kierować do nich, **póki są osiągalni**.

### Obszar 5: encoding / ffmpeg

Jedyny obszar, gdzie Shadowghost **nie** dominuje.

| osoba | commity | aktywność | ostatni commit | tematyka |
|---|---|---|---|---|
| **nyanmisaka** | 12 w `Controller/MediaEncoding` | 4 → 5 → 12 → 3 | 2026-07-18 | ffmpeg, akceleracja sprzętowa, DLNA, `EncodingHelper` |
| **Bond_009** | 10 w `MB.MediaEncoding` | 5 → 10 → 10 → 9 | 2026-08-24 | **napisy** (`SubtitleEncoder`), probing, enkoder |
| gnattu | 4 + 4 | 5 → 3 → 1 → 5 | 2026-09-06 | enkoder, testy encodingu, setup serwera |
| Piotr Niełacny | 4 | — | — | punktowo |

**Bus factor tutaj jest zdrowy: 27% / 13%.** nyanmisaka (od 2020, 195 commitów) — sprzęt i ffmpeg. Bond_009 (od 2018, **1018 commitów** — najdłuższy staż w repo) — napisy i probing.

## Klasyfikacja tematyczna kontrybutorów

| osoba | staż | commity 12m / łącznie | specjalizacja | status |
|---|---|---|---|---|
| **Shadowghost** | od 2020-03 | **396** / 740 | wszystko: repozytorium, encje, biblioteka, API, migracje, testy | **aktywny, dominujący** |
| theguymadmax | od 2024-08 | 115 / 160 | generalista rdzenia: `Item` + `Entities` + `Library` + `Providers` | aktywny, stabilny |
| JPVenson | od 2023-02 | 36 / 341 | **migracje EF Core, wieloproviderowość** | **wygasa** (P4 = 0) |
| nyanmisaka | od 2020-03 | 24 / 195 | ffmpeg, akceleracja sprzętowa, DLNA | aktywny |
| Bond_009 | od 2018-12 | 34 / **1018** | napisy, probing, enkoder — weteran | aktywny, wąsko |
| dkanada | od 2019-01 | 23 / 529 | API (`Controllers` 54), providery książek/komiksów | aktywny |
| Marc Brooks | od 2023-03 | 22 / 32 | **testy** (`Providers.Tests/ExternalId`), `Jellyfin.Extensions` | nowy w rdzeniu (od P3) |
| Tim Eisele | od b.d. | 18 / — | szeroko i płytko: biblioteka, EF, napisy, filtry | aktywny |
| gnattu | — | 14 / — | enkoder, testy encodingu | aktywny |
| TheMelmacian | od 2024-07 | 10 / 12 | zapytania: `Item` + `Model/Querying` + `Persistence` | wszedł w P3 |
| Cody Robibero | — | 20 / — | utrzymanie: migracje, filtry, backup, sortowanie | **najświeższy commit (2026-09-10)** |
| Niels van Velzen | — | 10 / — | API, użytkownicy | wygasa (P4 = 0) |

## Bus factor

Udział czołowego autora w commitach obszaru (kod, bez merge'y):

| obszar | udział #1 | autorów | ocena |
|---|---|---|---|
| `src/Jellyfin.Database` | **64%** Shadowghost | 13 | ryzyko wysokie |
| `Jellyfin.Server/Migrations` | **60%** Shadowghost | 16 | ryzyko wysokie + JPVenson wygasł |
| `MB.Controller/Entities` | **59%** Shadowghost | 18 | ryzyko wysokie |
| `ESI/Library` | **58%** Shadowghost | 30 | ryzyko wysokie |
| `JSI/Item` | **57%** Shadowghost | 31 | ryzyko wysokie |
| `src/Jellyfin.LiveTv` | 47% Shadowghost | 16 | umiarkowane |
| `Jellyfin.Api/Controllers` | 44% Shadowghost | 38 | umiarkowane |
| `MB.Controller/MediaEncoding` | 27% nyanmisaka | 17 | **zdrowe** |
| `MB.MediaEncoding` | 13% Bond_009 | 32 | **zdrowe** |

**Jedna osoba (Shadowghost) jest czołowym autorem w 7 z 9 obszarów** i odpowiada za 396 z ~900 commitów kodu w oknie. Ich aktywność rośnie: 7 → 107 → 112 → 170 na kwartał. Ponad połowa ich dorobku z sześciu lat (740 commitów) powstała w ostatnim roku.

Encoding to jedyna część repo z rozłożoną wiedzą.

## Rozstrzygnięte unknowns z artefaktów 1–2

| pytanie | odpowiedź |
|---|---|
| **Kto stoi za falą API w P3?** | Rozproszona, ale prowadzona przez Shadowghost (22 z 40 commitów w `Api/Controllers`), z dkanada (8) i TheMelmacian (5). Nie był to jednorazowy kontrybutor — to część szerszej przebudowy prowadzonej przez rdzeń |
| **Czy LiveTv jest osierocone?** | **Nie.** Wybuch w P2–P3 to Shadowghost (14 z 20 commitów), którzy nadal są aktywni. Obszar nie stracił właściciela — właściciel przeszedł do innych zadań. Ryzyko niższe, niż sugerowała sama historia churnu |
| **Czy skok testów w P3–P4 to zmiana polityki?** | **Nie — to inicjatywa jednej osoby.** W P4 Shadowghost ma 79 z ~100 commitów w `tests/`. Brak śladu zmiany wymogów w `.github/`. Trend jest kruchy: zależy od jednej osoby |
| **Plan wygaszenia `ESI`?** | Brak sygnału. `ESI/Library` jest aktywnie rozwijane przez te same osoby co `JSI` — nic nie wskazuje na migrację legacy |

## Do kogo z czym iść

| pytanie | osoba | uzasadnienie |
|---|---|---|
| cokolwiek o rdzeniu (encje, repozytorium, biblioteka, API) | **Shadowghost** | 59%/57%/58%/44% commitów; najszersza wiedza w repo |
| migracje EF Core, wieloproviderowość, PostgreSQL | **JPVenson** | autor `readme.md` migracji, 42 commity w rutynach — **kontaktować się szybko, aktywność wygasła w P4** |
| ffmpeg, akceleracja sprzętowa, transkodowanie | **nyanmisaka** | 12 commitów w `Controller/MediaEncoding`, staż od 2020 |
| napisy, probing mediów | **Bond_009** | 12 commitów w `Subtitles`, 1018 commitów w repo — najdłuższy staż |
| kontrakt API, providery książek | **dkanada** | 54 commity w `Controllers`, staż od 2019 |
| kontrakt zapytań (`InternalItemsQuery`, `Model/Querying`) | **TheMelmacian** | jedyni poza czołówką łączący `Item` + `Querying` + `Persistence` |
| testy, `Jellyfin.Extensions` | **Marc Brooks** | 9 commitów w `Providers.Tests`, weszli w P3 z profilem testowym |
| drugie zdanie / świeży kontekst utrzymaniowy | **Cody Robibero** | najświeższy commit w repo (2026-09-10), profil przekrojowy |

## Unknowns

- **Czy JPVenson odszedł, czy ma przerwę?** Historia pokazuje zero commitów w P4, nie powód. Przed zmianami w warstwie bazy warto potwierdzić dostępność.
- **Dlaczego Shadowghost ruszyli z 7 na 107 commitów między P1 a P2?** Zmiana roli, etatu, finansowania — repo nie odpowiada. Ma znaczenie dla oceny trwałości obecnego tempa.
- **Czy 396 commitów to jedna osoba, czy konto zespołowe?** Nie da się rozstrzygnąć z historii.
- **Review, nie autorstwo.** Analiza liczy tylko `author`. Osoby robiące code review (często najgłębiej znające obszar) są niewidoczne. Do uzupełnienia przez API GitHuba, jeśli potrzebne.
- **Dostępność ≠ aktywność.** Commity mówią, kto pisał kod, nie kto odpowie na pytanie. Weterani o niskim churnie (Bond_009, dkanada) mogą mieć wiedzę szerszą, niż wynika z ostatnich 12 miesięcy.
