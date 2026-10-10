# Worked example: #27926 and !16791 (October 2026)

- **Problem.** On GHC master and the 10.0 branch, configuring with `--with-system-libffi
  --with-ffi-libraries` left the RTS's `library-dirs-static` with only libffi's directory.
  Linking failed with `cannot find -lnuma/-ldw/-lelf` outside Nix. On macOS with IPE
  compression, even the GHC build failed (`ld: library 'zstd' not found`).
- **History.** `git log -- rts/rts.buildinfo.in` pointed to `1ac1a541` (!14935, which made GHC
  link with `library-dirs-static`) and `0f53ccc6` (!14996, which added
  `extra-lib-dirs-static: @FFILibDir@`). `git show origin/ghc-9.14:rts/rts.buildinfo.in` showed
  that 9.14 had neither.
- **Duplicate check.** Searching issues and MRs for `library-dirs-static`,
  `extra-lib-dirs-static`, `rts.buildinfo` and `cannot find -lnuma` found nothing.
- **Root cause.** In Cabal, `extraLibDirsStaticOrFallback`
  (`Distribution/Simple/Register.hs`) falls back to `extra-lib-dirs` only when no static dirs are
  given.
- **Fix.** Delete the one line. A three-line comment was drafted next to it, then dropped as
  noise.
- **Tests.**
  - Before and after on master, each in a fresh build root: on Linux in a nixpkgs dev shell, and
    on macOS with the wiki's configure line.
  - A counterfactual: also deleting `extra-lib-dirs` gave `cannot find -lffi`.
  - nixpkgs' wasm cross pipelines on aarch64-linux and aarch64-darwin.
- **Order.**
  1. File issue #27926.
  2. Amend the commit with `Fixes #27926.`.
  3. Push to the fork.
  4. Open MR !16791, titled with the commit subject.
- **CI.** The full-build jobs failed after about 40 s with `fatal: early EOF` while fetching the
  fork, an infrastructure problem. `lint-changelog` fails until a triager sets ~"no-changelog".
- **Lessons.**
  - Make the smallest change, with a short commit message.
  - Test from fresh build roots.
  - Check what CI covers before writing "CI can't catch this".
