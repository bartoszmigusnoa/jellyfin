# Artefakt 1 — Terytorium (historia gita)

**Repo:** jellyfin (backend serwera, .NET 10)
**Okno analizy:** 2025-09-12 → 2026-09-10 (12 miesięcy)
**Wygenerowano:** 2026-09-12
**HEAD:** `1d7b6d9784`

## Metoda

- `git log --since="12 months ago" --no-merges`, 2252 commity w oknie (1026 dotyka kodu po filtrze).
- **Metryka:** *touch* = liczba commitów, w których plik został zmieniony. Agregacja katalogu = suma touchy plików **bezpośrednio** w nim (nierekurencyjnie). Tam, gdzie podaję "commity", liczba jest **rekurencyjna** (z podkatalogami) — stąd rozbieżności typu `ESI/Library` 125 touchy vs 153 commity.
- **Odfiltrowany szum:** `*.json` (Weblate), `*.props`, `*.csproj`, `*.sln`, `*.md`, `*.yml`/`*.yaml`, `.github/**`, `deployment/**`, `.vscode`/`.devcontainer`/`.config`, `*.Designer.cs`, `*ModelSnapshot.cs`, `.editorconfig`, `.gitignore`, `*.lock`, `*.xml`, `*.txt`, `*.sh`, `*.ps1`, `*.svg`, `*.png`. Zostało 926 unikalnych plików.
- **Korekta renameów:** `-M --name-status`, pozycje `R100` (czysty rename, zero zmian treści) odrzucone. Bez tej korekty commit `f73fc1fe` zawyżał wyniki — patrz sekcja "Pułapki".
- Analiza sprzężeń: commity >8 katalogów odrzucone jako hurtowe (18 z 1026).

Skróty: `JSI` = Jellyfin.Server.Implementations, `ESI` = Emby.Server.Implementations, `MB` = MediaBrowser, `JDB` = src/Jellyfin.Database.

## A. TOP 10 obszarów (cały rok, po korekcie renameów)

| # | Katalog | Touch | Commity (rek.) |
|---|---|---|---|
| 1 | `JSI/Item` | 279 | 208 |
| 2 | `Jellyfin.Api/Controllers` | 228 | 125 |
| 3 | `MB.Controller/Entities` | 147 | 107 |
| 4 | `ESI/Library` | 125 | 153 |
| 5 | `Jellyfin.Server/Migrations/Routines` | **92** | 74 |
| 6 | `JDB.Providers.Sqlite/Migrations` | 61 | — |
| 7 | `MB.Controller/Library` | 59 | — |
| 8 | `MB.Controller/MediaEncoding` | 49 | 43 |
| 9 | `tests/JSI.Tests/Item` | 48 | — |
| 10 | `MB.Providers/Plugins/Tmdb/TV` | 42 | 35 |

Poziom projektu dawał generyki (`MB.Controller` 399, `ESI` 391), więc zejście na katalog było konieczne.

## B. TOP 10 plików (cały rok)

| # | Plik | Zmiany |
|---|---|---|
| 1 | `JSI/Item/BaseItemRepository.cs` | 81 |
| 2 | `ESI/Library/LibraryManager.cs` | 73 |
| 3 | `MB.Controller/Entities/Folder.cs` | 40 |
| 4 | `JSI/Item/BaseItemRepository.TranslateQuery.cs` | 40 |
| 5 | `MB.Controller/MediaEncoding/EncodingHelper.cs` | 38 |
| 6 | `MB.Controller/Entities/BaseItem.cs` | 35 |
| 7 | `JSI/Item/PeopleRepository.cs` | 31 |
| 8 | `MB.Controller/Library/ILibraryManager.cs` | 29 |
| 9 | `MB.MediaEncoding/Subtitles/SubtitleEncoder.cs` | 27 |
| 10 | `ESI/Dto/DtoService.cs` | 26 |

Ranking plików korekta renameów nie zmieniła — przemianowane pliki migracji (15–20 zmian) i tak były pod progiem.

## C. Nacisk pracy w czasie (okna 3-miesięczne)

| Okno | Zakres | Commity |
|---|---|---|
| P1 | 2025-09-12 → 12-12 | 275 |
| P2 | 2025-12-12 → 2026-03-12 | 319 |
| P3 | 2026-03-12 → 06-12 | 481 |
| P4 | 2026-06-12 → 09-11 | 566 |

Wolumen rośnie 2× przez rok — liczby bezwzględne wymagają normalizacji.

### Projekty × kwartał (touche, po korekcie)

| Projekt | P1 | P2 | P3 | P4 | Σ |
|---|---|---|---|---|---|
| MB.Controller | 43 | 121 | 117 | 118 | 399 |
| ESI | 49 | 74 | 132 | 136 | 391 |
| JSI | 51 | 84 | 109 | 108 | 352 |
| tests | 19 | 24 | 101 | **191** | 335 |
| MB.Providers | 37 | 46 | 106 | 122 | 311 |
| Jellyfin.Api | 27 | 55 | **123** | 57 | 262 |
| Jellyfin.Server | 36 | 61 | **33** | 48 | **178** |
| JDB | 15 | 50 | 51 | 42 | 158 |
| MB.Model | 7 | 17 | 46 | 29 | 99 |
| MB.MediaEncoding | 10 | 11 | 36 | 35 | 92 |
| src/Jellyfin.LiveTv | 2 | 23 | 28 | 12 | 65 |

### TOP 5 katalogów per kwartał

- **P1** — `JSI/Item` 36, `Api/Controllers` 25, `Migrations/Routines` 22, `ESI/Library` 20, `Entities` 19.
- **P2** — `JSI/Item` 78, `Entities` 59, `Api/Controllers` 43, `Migrations/Routines` 33, `ESI/Library` 29.
- **P3** — `Api/Controllers` 114, `JSI/Item` 73, `Sqlite/Migrations` 38, `ESI/Library` 37, `MB.Controller/Library` 32. (`Migrations/Routines` spada na 18, poz. 10.)
- **P4** — `JSI/Item` 92, `Api/Controllers` 46, `tests/JSI.Tests/Item` 43, `ESI/Library` 39, `Entities` 37.

### Wnioski

1. **Testy — jedyna wyraźna zmiana trendu.** Touche/commit: 0.07 → 0.08 → 0.21 → **0.34**. Pięciokrotny wzrost po normalizacji, więc nie efekt wolumenu. W P4 `tests/JSI.Tests/Item` to trzeci najgorętszy katalog w repo.
2. **Migracja warstwy danych na EF Core to dominujący wątek całego roku.** `BaseItemRepository*` 26 → 60 → 46 → 66. W P2 skupione w jednym pliku (50/60), od P3 rozbite na partiale (`TranslateQuery`, `Querying`, `QueryBuilding`, `ByName`). Rozbicie pliku nie zmniejszyło nacisku — obszar niedokończony.
3. **Fala w `Jellyfin.Api` w P3 była jednorazowa, nie trendem.** 0.10 → 0.17 → 0.28 → 0.10 touch/commit. Współbieżna z `MB.Model` (46) i `Integration.Tests/Controllers` — skoordynowana zmiana kontraktu API, zamknięta w P3.
4. **MediaEncoding budzi się w P3 i zostaje** (10/11 → 36/35). Niezależny front, bez sprzężenia z wątkiem bazodanowym.
5. **LiveTv: wybuch w P2–P3 (23, 28), wygaśnięcie w P4 (12).** Wzorzec "ktoś przyszedł, zrobił, odszedł" — kandydat na obszar bez aktywnego właściciela. → `unknowns`.
6. **Stały rdzeń:** `ESI/Library` (20/29/37/39) i `MB.Controller/Entities` nigdy nie stygną, nigdy nie dominują. Hot spoty strukturalne (god objects), nie fronty pracy.

## D. Sprzężenia (co zmienia się razem)

### Pary — support / conf A→B / conf B→A

| n | A→B | B→A | Para |
|---|---|---|---|
| 33 | 31% | 16% | `ESI/Library` + `JSI/Item` |
| 31 | 16% | 33% | `JSI/Item` + `MB.Controller/Entities` |
| 30 | 28% | **86%** | `ESI/Library` + `MB.Controller/Library` |
| 26 | 13% | **100%** | `JSI/Item` + `MB.Controller/Persistence` |
| 24 | 12% | **80%** | `JSI/Item` + `tests/JSI.Tests/Item` |
| 24 | 21% | 12% | `Api/Controllers` + `JSI/Item` |
| 21 | 20% | **81%** | `ESI/Library` + `MB.Controller/Persistence` |
| 19 | 54% | 73% | `MB.Controller/Library` + `MB.Controller/Persistence` |
| 16 | **100%** | 70% | `JDB/ModelConfiguration` + `JDB.Sqlite/Migrations` |

### Trójki

| n | Trójka |
|---|---|
| 17 | `ESI/Library` + `JSI/Item` + `MB.Controller/Library` |
| 17 | `ESI/Library` + `JSI/Item` + `MB.Controller/Persistence` |
| 16 | `JSI/Item` + `MB.Controller/Library` + `MB.Controller/Persistence` |
| 15 | `ESI/Library` + `MB.Controller/Library` + `MB.Controller/Persistence` |
| 8 | `Api/Controllers` + `JSI/Item` + `MB.Controller/Entities` |
| 8 | `JSI/Item` + `JDB/ModelConfiguration` + `JDB.Sqlite/Migrations` |

Cztery czołowe trójki to permutacje jednego zbioru: **`ESI/Library` + `JSI/Item` + `MB.Controller/Library` + `MB.Controller/Persistence`**. To jeden klaster zmian, nie cztery obszary.

### Wnioski dla TOP 3

**`JSI/Item` (200 commitów) — hub, nie liść.** Rozlewa się na 8 katalogów, żaden nie dominuje (max 16%), ale zależności są jednostronne: `MB.Controller/Persistence` w **100%** swoich commitów idzie z `Item`, `MB.Controller/Library` w 63%, `JDB.Implementations` w 50%. Interfejsy persystencji nigdy nie zmieniają się samodzielnie — ciągnie je implementacja. Odwrotność zdrowego kierunku (kontrakt powinien być stabilniejszy od implementacji). **Praktycznie: dotykasz `BaseItemRepository` → licz się z `IItemRepository`, `ILibraryManager` i migracją EF w tym samym PR.** Plus: `tests/JSI.Tests/Item` w 80% swoich commitów towarzyszy zmianie.

**`Jellyfin.Api/Controllers` (112 commitów) — najluźniej sprzężony z trójki.** Najsilniejszy partner to 21%. Warstwa w miarę odseparowana. Ale asymetria zdradza kierunek: `tests/Jellyfin.Api.Tests/Controllers` **83%**, `Api/Helpers` 39%, `MB.Controller/Persistence` 35% swoich commitów jadą z kontrolerami. Kontrolery są **odbiorcą** zmian z dołu, rzadziej źródłem — potwierdza interpretację fali P3.

**`MB.Controller/Entities` (93 commity) — rozsadnik zmian w dół.** 33% jego commitów dotyka `JSI/Item`, 25% `ESI/Library`, 17% `Api/Controllers`; w drugą stronę słabo (16/21/14%). `BaseItem`/`Folder` zmieniają się rzadziej niż konsumenci, ale gdy się zmienią — promieniują szeroko. Dodatkowo `tests/Jellyfin.Controller.Tests/Entities` 75% i `Entities/Movies` 86% to doczepki.

**Osobno: `JDB/ModelConfiguration` → `JDB.Sqlite/Migrations` = 100%.** Poprawne i oczekiwane. Dziś provider jest jeden, więc sprzężenie 1:1. Po dodaniu PostgreSQL to węzeł, w którym najłatwiej o zapomnianą migrację (`CLAUDE.md`: migracja musi powstać dla *każdego* providera).

## E. Wspólny mianownik całego repo

Analiza **bez filtra szumu**: dla każdego pliku liczba różnych obszarów, z którymi współzmienia się w jednym commicie (odrzucone commity >60 plików).

| total | solo | 2–5 plików | >5 plików | plik |
|---|---|---|---|---|
| 93 | **83** | 5 | 5 | `Directory.Packages.props` |
| 27 | 10 | 15 | 2 | `CONTRIBUTORS.md` |
| 21 | **0** | 3 | **18** | `JDB.Sqlite/Migrations/JellyfinDbModelSnapshot.cs` |
| 6 | **0** | 2 | 4 | `ESI/Localization/Core/en-US.json` |
| 3 | 0 | 0 | 3 | `SharedVersion.cs` |

**`Directory.Packages.props` to fałszywy trop** — największy "spread" (28 obszarów, 73 katalogi), ale 83 z 93 zmian to commity jednoplikowe (Renovate). Dotknął wszystkiego po kolei, nigdy *razem*. Odfiltrowanie słuszne.

**Prawdziwy wspólny mianownik: `JellyfinDbModelSnapshot.cs`** — generowany snapshot modelu EF Core. **Zero commitów solo**, 18 z 21 zmian w commitach >5 plików, rozrzut na 37 katalogów. Nie jest źródłem zmiany, tylko jej śladem: każda modyfikacja schematu zostawia w nim odcisk, niezależnie od obszaru pochodzenia. **Użyteczny jako detektor** — jeśli PR go rusza, dotyka persystencji, choćby zmiana wyglądała lokalnie. Jako cel pracy bezwartościowy (plik generowany, nie edytować ręcznie).

Drugi, słabszy: **`Core/en-US.json`** — źródło tłumaczeń (reszta języków to output Weblate). 0 solo, ale tylko 6 zmian, sygnał cienki. Wzorzec: user-facing string → wpis w en-US → kaskada ~30 plików z Weblate w osobnych commitach.

## F. Pułapki — weryfikacja aktualności

Sprawdzono `git cat-file -e HEAD:<path>` dla 24 plików z rankingów. **21 istnieje, 3 nie.**

| plik z rankingu | co się stało |
|---|---|
| `Jellyfin.Server/Migrations/Routines/MigrateLibraryDb.cs` | rename, `f73fc1fe` 2026-05-15 |
| `Jellyfin.Server/Migrations/Routines/MigrateLinkedChildren.cs` | jw. |
| `.github/workflows/ci-openapi.yml` | rozbity na 4 pliki, `6b443bb2` 2026-03-25 |

Commit `f73fc1fe` "Update filenaming scheme to match EFCore one" to **masowa zmiana nazw 33 plików** (32× R100 czysty rename, 1× R096). Cały `Migrations/Routines` przeszedł na schemat `{timestamp}_{Nazwa}.cs`.

Aktualne ścieżki i liczby po `--follow`:

- `Routines/20250420200000_MigrateLibraryDb.cs` — 15 zmian
- `Routines/20260113120000_MigrateLinkedChildren.cs` — 20 zmian

Zmiany nazw w oknie, wg katalogu: `Migrations/Routines` **36**, `.github/workflows/openapi` 4, `MB.Providers/Plugins/ComicVine` 3, `JDB.Sqlite/Migrations` 2, `MB.Providers/Plugins/GoogleBooks` 2. Poza tymi katalogami renameów praktycznie nie było.

**Wpływ na wyniki (skorygowany w tym dokumencie):**

- `Migrations/Routines` w P3: **51 → 18** (spadek z poz. 3 na 10 w kwartale).
- `Migrations/Routines` Σ rok: **125 → 92**.
- `Jellyfin.Server` Σ rok: **211 → 178**, P3 **66 → 33**.
- Ranking plików i analiza sprzężeń: bez zmian.

**Zasada na dalszą pracę:** dla `Migrations/Routines` używać `git log --follow` per plik — bez tego historia urywa się na maju 2026. Dla reszty repo zbędne.

## G. Unknowns

- **Czy `JSI/Item` jest hubem strukturalnym, czy tylko czasowym?** Sprzężenia to korelacja w commitach, nie zależności w kodzie. Do rozstrzygnięcia w artefakcie 2 (graf zależności): czy `MB.Controller/Persistence` naprawdę zależy od implementacji, czy to tylko dyscyplina PR-ów.
- **Kto stoi za falą API w P3 i za wygasłym LiveTv?** Bez danych o autorach nie wiadomo, czy to ten sam człowiek, zespół, czy jednorazowy kontrybutor. → artefakt 3.
- **Czy skok testów w P3–P4 to zmiana polityki (wymóg review), czy pojedyncza inicjatywa?** Do sprawdzenia w historii `.github/` i w rozkładzie autorów.
- **Stan migracji EF Core.** `BaseItemRepository` nadal gorący po roku — nie wiadomo, czy to ogon dużej migracji, czy nowy stan permanentny. Brak danych o planie/roadmapie w repo.
- **`ESI` vs `JSI`** — dwa równoległe zestawy implementacji (legacy Emby vs nowy Jellyfin). Historia nie mówi, czy `ESI` jest aktywnie wygaszany, czy oba mają zostać. `ESI/Library` rośnie przez cały rok, co sugeruje raczej to drugie.
- Analiza obejmuje tylko gałąź `master` i wyklucza merge commity — praca w niescalonych gałęziach jest niewidoczna.
