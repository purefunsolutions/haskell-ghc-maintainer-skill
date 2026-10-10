{
  lib,
  runCommand,
  makeWrapper,
  runtimeShell,
  python3,
  curl,
  git,
  coreutils,
  gnused,
  src,
}:

runCommand "ghc-contribution-skill" { nativeBuildInputs = [ makeWrapper ]; } ''
  cp -r ${src} $out
  chmod -R u+w $out
  for f in $out/scripts/*.sh; do
    substituteInPlace "$f" --replace-fail '#!/usr/bin/env bash' '#!${runtimeShell}'
  done
  for f in $out/scripts/*.py; do
    substituteInPlace "$f" --replace-fail '#!/usr/bin/env python3' '#!${python3}/bin/python3'
  done
  for f in $out/scripts/*; do
    wrapProgram "$f" --prefix PATH : ${
      lib.makeBinPath [
        python3
        curl
        git
        coreutils
        gnused
      ]
    }
  done
''
