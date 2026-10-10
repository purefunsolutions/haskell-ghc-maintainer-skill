self:
{
  config,
  lib,
  pkgs,
  ...
}:

let
  cfg = config.programs.ghc-contribution-skill;
  skill = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
  has = agent: lib.elem agent cfg.agents;
in
{
  options.programs.ghc-contribution-skill = {
    enable = lib.mkEnableOption "the ghc-contribution skill for coding agents";
    agents = lib.mkOption {
      type = lib.types.listOf (
        lib.types.enum [
          "claude"
          "agents"
          "opencode"
        ]
      );
      default = [
        "claude"
        "agents"
        "opencode"
      ];
      description = ''
        Skill directories to link the skill into: "claude" (~/.claude/skills, Claude Code),
        "agents" (~/.agents/skills: Codex, Pi, Cline, Zed, Warp and others) and "opencode"
        (~/.config/opencode/skills).
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    home.file = lib.mkMerge [
      (lib.mkIf (has "claude") { ".claude/skills/ghc-contribution".source = skill; })
      (lib.mkIf (has "agents") { ".agents/skills/ghc-contribution".source = skill; })
    ];
    xdg.configFile = lib.mkIf (has "opencode") {
      "opencode/skills/ghc-contribution".source = skill;
    };
  };
}
