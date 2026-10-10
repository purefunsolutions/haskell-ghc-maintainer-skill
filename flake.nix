{
  description = "Agent skill for contributing to GHC upstream (Claude Code, Codex, OpenCode, Pi and others)";

  # Any recent nixpkgs works; this is a stable branch. Share yours with `inputs.nixpkgs.follows`.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-26.05-darwin";

  outputs =
    { self, nixpkgs }:
    let
      inherit (nixpkgs) lib;
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
      src = ./skills/ghc-contribution;
    in
    {
      # The skill directory, with its scripts wrapped so curl, git and python3 come from Nix.
      packages = forAllSystems (pkgs: rec {
        ghc-contribution = pkgs.callPackage ./nix/skill.nix { inherit src; };
        default = ghc-contribution;
      });

      # `nix run .#install -- [claude] [agents] [opencode]` links the skill into the agents'
      # skills directories, behind a GC root so garbage collection can't remove it.
      apps = forAllSystems (
        pkgs:
        let
          skill = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
          install = pkgs.writeShellScriptBin "install-ghc-contribution-skill" ''
            set -euo pipefail
            root="''${XDG_STATE_HOME:-$HOME/.local/state}/ghc-contribution-skill"
            mkdir -p "$(dirname "$root")"
            nix-store --add-root "$root" --realise ${skill} > /dev/null
            exec ${pkgs.runtimeShell} ${./install.sh} --source "$root" "$@"
          '';
          app = {
            type = "app";
            program = "${install}/bin/install-ghc-contribution-skill";
          };
        in
        {
          install = app;
          default = app;
        }
      );

      checks = forAllSystems (pkgs: {
        skill = pkgs.callPackage ./nix/check.nix {
          inherit src;
          skill = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
        };
      });

      # Home Manager: programs.ghc-contribution-skill = { enable = true; agents = [ ... ]; };
      homeManagerModules.default = import ./nix/home-manager.nix self;
    };
}
