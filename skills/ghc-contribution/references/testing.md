# Building and testing GHC changes

Sources: `hadrian/README.md`, `hadrian/src/Hadrian/Haskell/Cabal/Parse.hs`, and the wiki pages
`building/hadrian`, `building/preparation/mac-osx` and `building/running-tests`.

## Layout

- The sequence is `./boot`, `./configure …`, then `hadrian/build -j`. Hadrian is built from the
  same source tree.
- `_build/stage0/bin/ghc` is the stage-1 compiler. `_build/stage1/bin/ghc` is the stage-2
  compiler, which uses the libraries in `_build/stage1/lib`.
- Packages are registered in `_build/stage1/lib/package.conf.d/<pkg>-<version>.conf` (installed
  form) and in `_build/stage1/inplace/package.conf.d/` (in-place form).
- Faster builds: `--flavour=quick` (plus `+no_dynamic_libs+no_dynamic_ghc`), and `--docs=none`.
- One test: `hadrian/build test --only=<name>`. Tests live in `testsuite/tests/**/all.T`.

## Pitfalls

- **Use a fresh `--build-root` for each variant** (before and after the change). Hadrian
  caches each package's description: `resolveContextData` is an `addOracleCache` that tracks only
  `setup-config`, and it reads configure-generated `*.buildinfo` files untracked. Nor does it
  rerun a package's configure step when only a `*.buildinfo.in` changes. So an incremental
  rebuild can keep the old registration, even after `rm -rf _build/stage1/<pkg>`.
- Test linking from a clean environment, e.g.
  `env -i HOME=$HOME PATH=/usr/bin:/bin _build/stage1/bin/ghc Hello.hs`. Nix shells add `-L`
  flags through `NIX_LDFLAGS`, which hides library-path bugs.
- Compare before and after with the same configure flags, and keep the outputs for the issue.
- To answer "why not change X as well?", a counterfactual build helps: change X too and show
  what breaks.
- Check every consumer of a field. Grep for the Haskell identifiers too (e.g. `LibDirsStatic`),
  not just the field name, in `compiler/`, `hadrian/src/`, `utils/ghc-pkg/` and `libraries/`.

## Environments

- **Nix:** nixpkgs' GHC derivations provide a ready build environment, e.g.
  `nix-shell <nixpkgs> -A haskell.compiler.ghcHEAD`. With `__structuredAttrs`, `configureFlags` is
  a bash array there, so source your build script inside the shell rather than running it as a
  child process. nixpkgs builds hadrian from the GHC tree being built
  (`pkgs/development/tools/haskell/hadrian/make-hadrian.nix`).
- **macOS:** the wiki page `building/preparation/mac-osx` gives `./configure --with-system-libffi
  --with-intree-gmp --with-ffi-libraries=$sdk_path/usr/lib --with-ffi-includes=$sdk_path/usr/include/ffi`,
  where `sdk_path=$(xcrun --sdk macosx --show-sdk-path)`. `--enable-ipe-data-compression` also
  needs `pkg-config`, for the libzstd version check.
- **Low bandwidth:** `git clone --depth 1 --recurse-submodules --shallow-submodules` keeps the
  download to a few hundred MB. Ask before downloading.

## Shell pitfalls (when the user's shell is zsh)

- `$var:r…` and `$var:h…` are history modifiers. Write `"${var}:path"`.
- A word starting with `=` is expanded as a command path, so `echo ====` fails.
- An unquoted `$var` isn't word-split. `cmd | tail` hides `cmd`'s exit status.
- `pgrep -f <pattern>` also matches the shell that runs the check, if the pattern is in its
  command line.
