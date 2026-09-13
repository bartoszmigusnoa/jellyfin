# Analizator zależności .NET

Skrypty użyte do zbudowania `../artifact-2-structure.md`. `dependency-cruiser` z oryginalnego
promptu obsługuje wyłącznie JS/TS, więc graf dla .NET budowany jest z `ProjectReference`
(`*.csproj`) oraz dyrektyw `namespace`/`using` w plikach `.cs`.

## Użycie

Uruchamiaj z dowolnego katalogu, w kolejności:

```bash
python3 build-graph.py        # -> .cache/graph.json
python3 analyze-projects.py   # warstwy, cykle i fan-in projektów
python3 analyze-dirs.py       # fan-in/fan-out katalogów -> .cache/edges.json
python3 analyze-cycles.py     # cykle 2- i 3-elementowe
```

Root repo wykrywany jest ze ścieżki skryptu. Nadpisanie: `JF_REPO=/sciezka/do/repo`,
katalog wyjściowy: `JF_OUT=/sciezka`.

## Ograniczenia

Widoczne są tylko dyrektywy `using`. Poza zasięgiem pozostają: typy używane przez pełną
nazwę kwalifikowaną, generyki rozwiązywane w runtime oraz wiązanie przez DI i refleksję
(`ApplicationHost.DiscoverTypes`). Wyniki fan-in/fan-out to dolne oszacowanie.
