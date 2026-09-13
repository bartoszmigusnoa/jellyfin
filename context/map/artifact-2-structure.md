# Artefakt 2 — Struktura (graf zależności)

**Repo:** jellyfin (backend serwera, .NET 10)
**Wygenerowano:** 2026-09-12
**HEAD:** `1d7b6d9784`
**Wejście:** `context/map/artifact-1-territory.md`

## Podmiana narzędzia

`dependency-cruiser` obsługuje wyłącznie JS/TS (ESM/CJS/AMD). Dla .NET jest nieużyteczny. Sprawdzone alternatywy:

| narzędzie | werdykt |
|---|---|
| NDepend | najpełniejsze, ale komercyjne (licencja per-seat) |
| `dotnet-sonarscanner` (obecny globalnie) | wymaga serwera SonarQube/SonarCloud — za ciężkie na rozpoznanie |
| `ilspycmd` (obecny globalnie) | dekompilacja IL — zbędna, mamy źródła |
| Roslyn + `Microsoft.CodeAnalysis` | dokładne, ale wymaga kompilacji całego solution |

**Wybór: własny analizator statyczny** na parsowaniu źródeł. Cztery skrypty w `context/map/tools/`:

| skrypt | rola |
|---|---|
| `build-graph.py` | `ProjectReference` z 43 `.csproj` + `namespace`/`using` z 2110 plików → `graph.json` |
| `analyze-projects.py` | cykle i warstwy na poziomie projektów, fan-in |
| `analyze-dirs.py` | graf katalog→katalog (przez mapowanie namespace→katalog), fan-in/fan-out |
| `analyze-cycles.py` | cykle 2- i 3-elementowe, filtrowane do obszarów z artefaktu 1 |

**Ograniczenia metody (ważne przy czytaniu wyników):** analizowane są tylko dyrektywy `using`. Nie widać: typów użytych przez pełną nazwę kwalifikowaną, generyków rozwiązywanych w runtime, **a przede wszystkim wiązań przez DI**. W Jellyfin to ostatnie jest kluczowe — patrz obserwacja 1.

## Pomysły na eksplorację (co ten graf umie odpowiedzieć)

1. **Warstwy i ich naruszenia** — czy `ProjectReference` tworzy DAG i czy kierunek zależności zgadza się z deklarowaną architekturą (`Model` → `Common` → `Controller` → implementacje).
2. **Cykle wewnątrz projektu** — MSBuild blokuje cykle między projektami, więc cały splątany dług siedzi *wewnątrz* assembly, na poziomie namespace'ów. Tam trzeba szukać.
3. **Rozjazd struktura↔historia** — porównanie fan-in/fan-out z rankingiem churnu z artefaktu 1. Miejsca o wysokim churnie i zerowym fan-in to kod wiązany w runtime, którego żadna analiza statyczna nie pilnuje.

## Najważniejsze obserwacje

1. **Graf projektów jest czystym DAG-iem — zero cykli, 10 warstw.** Architektura na poziomie assembly jest zdyscyplinowana i wymuszona przez MSBuild.
2. **Najgorętszy obszar repo (`JSI/Item`, 279 touchy, #1 w artefakcie 1) ma fan-in = 5.** Strukturalnie prawie nikt od niego nie zależy. Wszystkie sprzężenia czasowe z artefaktu 1 (`ESI/Library`, `Api/Controllers`, `MB.Controller/Entities`) mają **zero** krawędzi strukturalnych. Kod jest wiązany wyłącznie przez interfejsy + DI.
3. **Pytanie z artefaktu 1 rozstrzygnięte: sprzężenie `MB.Controller/Persistence` → `JSI/Item` (100%) NIE jest strukturalne.** Kierunek jest odwrotny (11 plików `Item` → `Persistence`), a odwrotny być nie może, bo `MB.Controller` leży warstwę niżej (L5 vs L6). To dyscyplina PR-ów, nie zależność kodu.
4. **`MediaBrowser.Controller` — warstwa kontraktów — jest wewnętrznie splątana.** 26 cykli 3-elementowych, wszystkie w jednym projekcie. `Entities` ↔ `Library`, `Entities` ↔ `Providers`, `Entities` ↔ `Persistence` to cykle wzajemne. Ta warstwa ma fan-in 14 projektów — czyli splątanie jest dziedziczone przez całe repo.
5. **`Jellyfin.Api/Controllers` ma fan-out 98 przy fan-in 2.** Największy konsument w repo, prawie nic od niego nie zależy. Struktura potwierdza wniosek z artefaktu 1: kontrolery są odbiorcą zmian, nie ich źródłem.

## Warstwy projektów

Graf `ProjectReference`, głębokość = najdłuższa ścieżka w dół. **Cykli: zero.**

| L | projekt | refs | fan-in |
|---|---|---|---|
| L9 | `Jellyfin.Server` | 7 | 0 |
| L8 | `Emby.Server.Implementations` | 13 | 1 |
| L7 | `Jellyfin.Api` | 4 | 1 |
| L6 | `Jellyfin.Server.Implementations` | 5 | 2 |
| L6 | `MediaBrowser.Providers`, `MediaBrowser.MediaEncoding`, `Jellyfin.LiveTv`, `Jellyfin.Drawing(.Skia)`, `Jellyfin.Networking`, `MediaBrowser.XbmcMetadata`, `MediaBrowser.LocalMetadata`, `Emby.Photos`, `Jellyfin.MediaEncoding.Hls` | 2–4 | — |
| L5 | `MediaBrowser.Controller` | 4 | **14** |
| L4 | `Jellyfin.Database.Providers.Sqlite`, `Emby.Naming` | 2 | — |
| L3 | `MediaBrowser.Common` | 1 | **11** |
| L2 | `MediaBrowser.Model` | 2 | **14** |
| L1 | `Jellyfin.Data` | 1 | 2 |

Trzy fundamenty (`Model` 14, `Controller` 14, `Common` 11) zbierają 39 z 94 krawędzi. Zgodne z opisem w `CLAUDE.md`.

## Cykle w aktywnych obszarach

Cykle na poziomie katalogów. **38 par wzajemnych** w całym repo, **26 cykli 3-elementowych** dotykających obszarów gorących. Wszystkie leżą wewnątrz pojedynczych projektów.

| Obszar | Co znalazłem | Dowód | Dlaczego to ważne przy zmianie | Związek z artefaktem 1 | Co sprawdzić dalej |
|---|---|---|---|---|---|
| `MB.Controller/Entities` ↔ `MB.Controller/Library` | cykl wzajemny, najcięższy w warstwie kontraktów | 6 plików w jedną, **22** w drugą stronę | `BaseItem`/`Folder` i `ILibraryManager` nie dają się zmienić osobno — każda zmiana sygnatury wraca rykoszetem. To ten sam klaster, który w historii ma 31 wspólnych commitów | `Entities` #3 (147), `MB.Controller/Library` #7 (59); para 31 commitów | czy da się wyciąć interfejs pośredni, czy `Folder` musi znać `ILibraryManager` |
| `MB.Controller/Entities` ↔ `MB.Controller/Providers` | cykl wzajemny, niemal symetryczny | 13 ↔ 15 plików | Model domenowy i kontrakty dostawców metadanych wiedzą o sobie nawzajem. Dodanie pola do encji potrafi wymusić zmianę w interfejsie providera | `Entities` #3; `MB.Controller/Providers` ma fan-in **92** | który kierunek jest przypadkowy — kandydat do odwrócenia |
| `MB.Controller/Entities` ↔ `MB.Controller/Persistence` | cykl wzajemny | 2 ↔ 7 plików | `IItemRepository` zna encje, encje znają persystencję. Zamyka pętlę kontraktów wokół warstwy danych | `Persistence` w 100% commitów idzie z `JSI/Item` | czy `Persistence`→`Entities` (7) to tylko typy zwracane |
| `MB.Controller` jako całość | **26 cykli 3-elementowych**, wszystkie wewnątrz projektu; `Entities` w 22 z nich | `analyze-cycles.py`, np. `Entities → LiveTv → Providers → Entities` | Warstwa abstrakcji ma fan-in 14 projektów. Splątanie w środku propaguje się na całe repo — nie ma bezpiecznego podzbioru do zmiany w izolacji | `Entities` #3 w churnie, „rozsadnik zmian w dół" (33%/25%/17%) | czy cykle idą przez typy, czy tylko przez `using` niewykorzystanych namespace'ów |
| `JDB.Implementations/Entities` ↔ `Interfaces` | najcięższy cykl liczbowo w repo | **27 ↔ 3** | Encje EF Core i ich interfejsy wzajemnie zależne. Przy dodaniu drugiego providera (PostgreSQL) ten węzeł trzeba będzie rozplątać jako pierwszy | `JDB` Σ 158; para `ModelConfiguration`↔`Sqlite/Migrations` = 100% | czy `Interfaces`→`Entities` (3) to `IHasPermissions`-style marker |
| `ESI/Library` ↔ `ESI/ScheduledTasks/Tasks` | słaby cykl (1↔1) | 1 plik w każdą stronę | Kosmetyczny, ale pokazuje, że zadania cykliczne i menedżer biblioteki są splecione | `ESI/Library` #4 (125), `ScheduledTasks/Tasks` w TOP 10 P4 | niski priorytet |
| `Emby.Naming/Common` ↔ `Emby.Naming/Video` | cykl wzajemny 1↔6 | 6 plików `Video`→`Common` | Parser nazw plików — mały projekt, ale cykl utrudnia testowanie rozpoznawania nazw w izolacji | `Emby.Naming` Σ 38, stabilny | niski priorytet |

**Czego NIE znaleziono:** żadnego cyklu przechodzącego przez `JSI/Item`, `Api/Controllers` ani `Migrations/Routines` — trzy z pięciu najgorętszych obszarów są strukturalnie czyste.

## Granice warstw

| Sprawdzana granica | Wynik | Dowód | Dlaczego to ważne przy zmianie | Związek z artefaktem 1 | Co sprawdzić dalej |
|---|---|---|---|---|---|
| `MediaBrowser.Model` jako fundament | **respektowana** | L2, fan-in 14, zależy tylko od `Jellyfin.Data` | DTO klientów są odizolowane. Zmiana w `Model` = zmiana kontraktu API dla wszystkich klientów Jellyfin | `MB.Model` skok w P3 (46) razem z falą `Jellyfin.Api` | czy skok w P3 to breaking change w API |
| `MB.Controller` poniżej implementacji | **respektowana** | L5; `JSI` (L6), `ESI` (L8), `Jellyfin.Api` (L7) — wszystkie wyżej | Kierunek zależności jest poprawny: implementacje znają kontrakty, nie odwrotnie | — | — |
| `MB.Controller/Persistence` → `JSI/Item` | **BRAK takiej zależności** | 0 plików; odwrotnie 11 plików `Item`→`Persistence` | **Rozstrzyga unknown z artefaktu 1.** Sprzężenie 100% w historii to nie zależność kodu — to praktyka zespołu (zmiana implementacji pociąga świadomą zmianę kontraktu) | para 26 commitów, conf B→A = 100% | czy interfejs jest przykrawany pod jedną implementację (anti-pattern: header interface) |
| `ESI` ↔ `JSI` (legacy vs nowe) | **jednokierunkowa**, `ESI` (L8) → `JSI` (L6) | `ESI` ma 13 refs, `JSI` 5 | Legacy zależy od nowego, nie odwrotnie. Wygaszanie `ESI` jest możliwe bez ruszania `JSI` | oba rosną przez cały rok (`ESI` 49→136, `JSI` 51→108) | czy `ESI` ma plan wygaszenia — brak sygnału w repo |
| `Jellyfin.Api` → warstwa danych | **pośrednia**, przez kontrakty | `Api/Controllers` fan-out 98, fan-in 2; zero krawędzi do `JSI/Item` | Kontrolery nie sięgają do repozytoriów bezpośrednio. Dobra granica — ale jednocześnie oznacza, że zmiana repozytorium nie zapali się w kompilatorze kontrolerów | `Api/Controllers` #2 (228); fala P3 | czy przez `IItemRepository` przechodzą typy EF-owe |
| Plug-iny jako granica | **brak granicy statycznej** | `ApplicationHost.GetComposablePartAssemblies()` + refleksja | Typy wtyczek wchodzą do tego samego `GetExportTypes<T>()` co rdzeń. Żadna analiza statyczna nie pokaże, kto naprawdę implementuje dany interfejs | — | inwentaryzacja implementacji kluczowych interfejsów |

## Rozjazd: struktura vs historia

Zestawienie churnu z artefaktu 1 z fan-in/fan-out z tego artefaktu. Najważniejsza tabela w dokumencie.

| Katalog | Churn (rank) | fan-in | fan-out | odczyt |
|---|---|---|---|---|
| `JSI/Item` | 279 (#1) | **5** | 24 | **gorący, strukturalnie niewidoczny** — wiązany przez DI |
| `Jellyfin.Api/Controllers` | 228 (#2) | 2 | **98** | czysty konsument, liść grafu |
| `MB.Controller/Entities` | 147 (#3) | **119** | 35 | gorący **i** centralny — najwyższe ryzyko |
| `ESI/Library` | 125 (#4) | 8 | 52 | gruby konsument, mały dostawca |
| `MB.Controller/Library` | 59 (#7) | **118** | 26 | centralny, umiarkowanie gorący |
| `MB.Controller/Persistence` | — | 42 | 9 | kontrakt, ciągnięty przez implementację |
| `Migrations/Routines` | 92 (#5) | **0** | 38 | całkowity liść — nic od niego nie zależy |
| `MB.Model/Entities` | — | **129** | — | najwyższy fan-in w repo, niski churn = zdrowe |

Trzy wzorce:

- **Gorące + centralne** (`MB.Controller/Entities`): najdroższe zmiany. Wysoki churn *i* 119 zależnych katalogów *i* 22 cykle.
- **Gorące + niewidoczne** (`JSI/Item`, `Migrations/Routines`): kompilator nie ostrzeże. Jedyną siatką bezpieczeństwa są testy — stąd skok `tests/JSI.Tests/Item` w P4 jest racjonalną reakcją, nie przypadkiem.
- **Zimne + centralne** (`MB.Model/Entities`, fan-in 129): fundament działa jak należy.

## Ryzyka testowalności

### Podsumowanie

Testowalność rozkłada się dokładnie odwrotnie do intuicji z grafu. Obszary strukturalnie czyste (`JSI/Item`) są łatwe do testowania jednostkowego — `BaseItemRepository` bierze 5 zależności w konstruktorze, wszystkie to interfejsy. Obszary splątane (`MB.Controller/Entities`, `ESI/Library`) są praktycznie nietestowalne w izolacji.

### Lista ryzyk testowych

| # | Ryzyko | Dowód | Rekomendacja |
|---|---|---|---|
| 1 | **`LibraryManager` — 24 zależności w konstruktorze, 4150 linii, fan-out 52** | `an4.py`; największa klasa nie-encoding w repo | Test jednostkowy wymaga 24 mocków. Preferować test integracyjny na realnym hoście |
| 2 | **`EncodingHelper` — 8019 linii, największy plik w repo** | 6 zależności w ctor, ale ogromna powierzchnia logiki | Testy tabelaryczne na budowanie argumentów ffmpeg; nie mockować ffmpeg, asertować stringi |
| 3 | **`BaseItem` — 3061 linii, zero zależności w ctor, fan-in 119** | model domenowy z logiką, 22 cykle | Nie da się testować „kawałka" — każdy test ciągnie cały graf encji. Kandydat na testy charakteryzujące przed refaktorem |
| 4 | **`SessionManager` — 13 zależności, 2267 linii** | fan-out 33 | Test integracyjny, nie jednostkowy |
| 5 | **`DtoService` — 11 zależności, 1806 linii** | wspólny mianownik serializacji | Wysokie ryzyko regresji przy zmianie encji; testy migawkowe DTO |
| 6 | **`Migrations/Routines` — fan-out 38, fan-in 0, brak testów** | `tests/` nie ma odpowiednika tego katalogu | Migracje są jednorazowe i nieodwracalne. Brak siatki to realne ryzyko — test na kopii bazy |
| 7 | **Wiązanie przez DI omija kompilator** | `JSI/Item` fan-in 5 przy churnie 279 | Zmiana sygnatury w repozytorium nie zapali się w `Api` ani `ESI`. Tylko testy i runtime to wyłapią |
| 8 | **Wtyczki ładowane refleksją** | `GetComposablePartAssemblies()` | Zmiana interfejsu publicznego psuje wtyczki poza repo. Żaden test w repo tego nie pokryje |

### Najbardziej podejrzane moduły

1. `Emby.Server.Implementations/Library/LibraryManager.cs` — 24 dep, 4150 linii, fan-out 52, churn #2 (73). Kumuluje wszystkie trzy metryki ryzyka.
2. `MediaBrowser.Controller/Entities/BaseItem.cs` — fan-in 119, 22 cykle, churn 35. Zmiana promieniuje najszerzej w całym repo.
3. `Jellyfin.Server.Implementations/Item/BaseItemRepository.*` — 3350 linii w 5 partialach, churn #1 (81 + 40 + 31 + 20 + 19 + 18). Testowalny (5 dep), ale ogromny i wciąż w ruchu.
4. `MediaBrowser.Controller/MediaEncoding/EncodingHelper.cs` — 8019 linii, churn 38, rosnący front od P3.

### Co sprawdzić dalej

- Czy 26 cykli w `MB.Controller` przechodzi przez realne typy, czy część to nieużywane `using` (łatwy zysk: usunięcie martwych importów rozwiązuje cykl bez refaktoru).
- Pokrycie testami `Migrations/Routines` — jedyny obszar TOP-10 bez odpowiednika w `tests/`.
- Czy `IItemRepository` przepuszcza typy EF Core do warstwy `Api` (przeciek abstrakcji przez granicę warstw).
- Inwentaryzacja implementacji kluczowych interfejsów przez refleksję — czego graf statyczny nie widzi.

### Opcjonalny kolejny krok: graf

Najbardziej wartościowy podgraf do renderu: **cykle wewnątrz `MediaBrowser.Controller`** — 26 cykli 3-elementowych wokół `Entities`, `Library`, `Providers`, `Persistence`. Jedno pytanie, na które odpowiada: *które krawędzie trzeba wyciąć, żeby rozplątać warstwę kontraktów?* Zakres: 10–12 katalogów, czytelne w SVG. Reszta repo na graf się nie nadaje — DAG projektów jest trywialny, a `JSI/Item` nie ma krawędzi do narysowania.

## Unknowns

- **Czy fan-in `JSI/Item` = 5 to zdrowie, czy ślepota metody?** Analiza widzi tylko `using`. Jeśli konsumenci sięgają przez `IItemRepository` (a sięgają), realne sprzężenie jest wyższe — ale przechodzi przez kontrakt, nie implementację. Do potwierdzenia inwentaryzacją wstrzykiwań.
- **Czy cykle w `MB.Controller` są zamierzone?** Model domenowy z zachowaniem (`BaseItem` znający `ILibraryManager`) to świadoma decyzja w wielu systemach medialnych. Historia nie mówi, czy to projekt, czy erozja.
- **Plan dla `ESI`.** Struktura pokazuje, że wygaszenie jest możliwe (jednokierunkowa zależność), ale churn rośnie. Brak deklaracji w repo.
- **Wpływ wtyczek.** Graf obejmuje wyłącznie kod w tym repo. Wtyczki zewnętrzne konsumują te same interfejsy i są niewidoczne dla całej analizy.
- Metoda nie widzi typów kwalifikowanych pełną nazwą ani generyków rozwiązywanych w runtime — liczby fan-in/fan-out są dolnym oszacowaniem.
