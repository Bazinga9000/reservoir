{
  description = "A puzzlehunt management webapp used by ℙoNDeterministic.";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
    process-compose-flake.url = "github:Platonic-Systems/process-compose-flake";
    services-flake.url = "github:juspay/services-flake";
  };
  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;
      imports = [
        inputs.process-compose-flake.flakeModule
      ];
      perSystem =
        {
          self',
          pkgs,
          config,
          lib,
          ...
        }:
        {
          process-compose."reservoir" =
            { config, ... }:
            {
              imports = [
                inputs.services-flake.processComposeModules.default
              ];

              services.redis."r1".enable = true;
            };
          packages.default = self'.packages.reservoir;

          devShells.default = pkgs.mkShell {
            inputsFrom = [
              # Add the packages of the enabled services in the devShell
              #
              # For example: `psql` to interact with `postgres` server or `redis-cli` with `redis-server`
              config.process-compose."reservoir".services.outputs.devShell
            ];
            packages = [
              # Add the process-compose app in the devShell
              #
              # In the devShell, run `reservoir` to run the app
              self'.packages.reservoir
            ];
          };
        };
    };
}
