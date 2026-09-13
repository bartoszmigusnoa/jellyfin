# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Jellyfin media server backend (ASP.NET Core, .NET 10, `global.json` pins SDK 10.0.0 with `rollForward: latestMinor`). The web client lives in a separate repo (`jellyfin-web`) and is not part of this tree.

## Commands

```bash
dotnet build                                   # build whole solution
dotnet format --verify-no-changes              # what CI format check runs
dotnet format                                  # apply formatting
dotnet test Jellyfin.sln                       # all tests
dotnet test tests/Jellyfin.Naming.Tests        # one test project
dotnet test --filter "FullyQualifiedName~VideoResolverTests"   # one class/test
dotnet run --project Jellyfin.Server --webdir /abs/path/to/jellyfin-web/dist
dotnet run --project Jellyfin.Server -- --nowebclient          # skip web client hosting
```

Server defaults to `http://localhost:8096`; Swagger at `/api-docs/swagger/index.html`. `ffmpeg` (jellyfin-ffmpeg) must be installed for any transcoding path. `JELLYFIN_NOWEBCONTENT=true` is the env equivalent of `--nowebclient`; the setup wizard cannot run without a hosted web client.

CI (`.github/workflows/`) runs `dotnet test Jellyfin.sln --configuration Release --settings tests/coverletArgs.runsettings` on Linux/macOS/Windows, plus `dotnet format --verify-no-changes`.

## Build constraints that break the build

- `TreatWarningsAsErrors=true` repo-wide (`Directory.Build.props`). Debug builds additionally enable `AnalysisMode=AllEnabledByDefault` plus StyleCop, SerilogAnalyzer, IDisposableAnalyzers, MultithreadingAnalyzer, BannedApiAnalyzers. A warning that only appears in Debug will still fail the build.
- Central package management: add/bump versions in `Directory.Packages.props`, not in individual `.csproj` files.
- `BannedSymbols.txt` bans `Task<T>.Result`, `Guid.op_Equality`/`op_Inequality`, and `Guid.Equals(object)` — use `await`, and `Guid.Equals(Guid)` / `IsEmpty` comparisons instead.
- Custom analyzer `src/Jellyfin.CodeAnalysis` — JF0001 (error): an `IAsyncDisposable` obtained via `await` must be disposed with `await using`, not `using`.
- `.editorconfig` (22k lines) is the style authority; file-scoped namespaces, 4-space indent, LF endings.

## Architecture

Composition happens at startup, not via a static container registry:

- `Jellyfin.Server/Program.cs` → parses `StartupOptions`, sets up paths/Serilog, runs pre-startup migrations, builds the generic host.
- `Emby.Server.Implementations/ApplicationHost.cs` (~1000 lines) is the real composition root. `DiscoverTypes()` reflects over a fixed list of core assemblies plus plugin assemblies (`GetComposablePartAssemblies`), caches every concrete type, and `GetExportTypes<T>()` / `Resolve<T>()` serve interface-keyed lookups from that cache. Adding a new `IX` implementation in a scanned assembly usually makes it discoverable without explicit registration; explicit singletons go in `RegisterServices`.
- `Jellyfin.Server/CoreAppHost.cs` subclasses it to add server-specific assemblies/services; `Startup.cs` wires the ASP.NET pipeline (middleware, auth policies, MVC).

Project layers:

- `MediaBrowser.Model` — DTOs/enums shared with clients (API surface types).
- `MediaBrowser.Common` / `MediaBrowser.Controller` — interfaces and abstractions; most `I*` contracts live here.
- `Emby.Server.Implementations` — legacy-rooted implementations of those contracts (library, sessions, scheduled tasks, plugins, syncplay, live TV hooks).
- `Jellyfin.Server.Implementations` — newer EF Core-backed implementations (users, devices, security, activity, trickplay, backup).
- `Jellyfin.Api` — controllers only; inherit `BaseJellyfinApiController` (gives `[Route("[controller]")]` and the camelCase/PascalCase JSON producers). Auth is policy-based: `Jellyfin.Api/Auth/*Policy` handlers + roles in `Constants/UserRoles.cs`, via `CustomAuthenticationHandler`.
- `MediaBrowser.Providers`, `MediaBrowser.LocalMetadata`, `MediaBrowser.XbmcMetadata` — metadata/image provider implementations; `Emby.Naming` parses filenames into media identity.
- `MediaBrowser.MediaEncoding` + `src/Jellyfin.MediaEncoding.Hls`/`.Keyframes` — ffmpeg argument building, HLS playlist generation, keyframe extraction.
- `src/Jellyfin.Drawing(.Skia)`, `src/Jellyfin.Networking`, `src/Jellyfin.LiveTv`, `src/Jellyfin.Extensions` — self-contained subsystems.

### Two distinct migration systems — do not conflate

1. **EF Core schema migrations**, per database provider. Each provider owns its own migration set; see `src/Jellyfin.Database/readme.md`:
   ```bash
   dotnet ef migrations add {NAME} --project "src/Jellyfin.Database/Jellyfin.Database.Providers.Sqlite" \
     --output-dir Migrations -- --migration-provider Jellyfin-SQLite
   ```
   A new migration must be created for *every* provider. `dotnet restore` first if `dotnet-ef` is missing (it's a local tool in `.config/dotnet-tools.json`).
2. **Jellyfin data/config migration routines** in `Jellyfin.Server/Migrations/`. Routines are classes tagged with `[JellyfinMigration(order, name)]`, named `Routines/{timestamp}_{Name}.cs`, ordered by the timestamp and bucketed into a `JellyfinMigrationStageTypes` stage (pre-startup / core init / app init). `PreStartupRoutines/` run before the host exists (config-file rewrites); `Routines/` run against the DB and services.

`JellyfinDbContext` lives in `src/Jellyfin.Database/Jellyfin.Database.Implementations`; entities and `ModelConfiguration` are there too. `Jellyfin.Data` holds query/DTO/enum types used against it.

### Plugins

`PluginManager` (`Emby.Server.Implementations/Plugins`) loads external assemblies into the type-discovery pass and calls `RegisterServices` on them, so plugin types participate in the same `GetExportTypes<T>()` resolution as core types. Plugin controllers are picked up via `GetApiPluginAssemblies()`.

## Tests

xUnit v3 with Moq and AutoFixture (`AutoFixture.Xunit3`, `AutoFixture.AutoMoq`). `tests/Jellyfin.Server.Integration.Tests` uses `Microsoft.AspNetCore.Mvc.Testing` against a real host — it is also where the OpenAPI spec is produced for the `openapi-*` workflows, so controller signature changes show up there.
