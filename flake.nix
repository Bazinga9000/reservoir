{
  description = "A puzzlehunt management webapp used by ℙoNDeterministic.";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";

    sajak = {
      url = "github:Bazinga9000/sajak";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;
      perSystem =
        {
          self',
          inputs',
          pkgs,
          config,
          lib,
          ...
        }:
        {
          devShells.default = pkgs.mkShell {
            packages = with pkgs; [
              uv
              redis
              process-compose
              inputs'.sajak.packages.default
            ];
          };
        };
    };
}
