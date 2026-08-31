{
  description = "A puzzlehunt management webapp used by ℙoNDeterministic.";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";

    sajak = {
      url = "github:Bazinga9000/sajak";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;
      flake.nixosModules.default = import ./nix/module.nix {
        app = inputs.self.packages.${inputs.systems}.reservoir;
        sajakModule = inputs.sajak.nixosModules.default;
      };
      perSystem =
        {
          self',
          inputs',
          pkgs,
          config,
          lib,
          ...
        }:
        let
          inherit (inputs.nixpkgs) lib;

          workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          overlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          pythonSet =
            (pkgs.callPackage inputs.pyproject-nix.build.packages {
              python = pkgs.python313;
            }).overrideScope
              (
                lib.composeManyExtensions [
                  inputs.pyproject-build-systems.overlays.wheel
                  overlay
                ]
              );

          # Virtualenv with the app's runtime dependencies (prod group included so gunicorn is available).
          virtualenv = pythonSet.mkVirtualEnv "reservoir-env" (
            workspace.deps.default // workspace.deps.groups
          );

          app = pkgs.stdenv.mkDerivation {
            pname = "reservoir";
            version = "0.1.0";
            src = ./.;
            dontBuild = true;

            installPhase = ''
              mkdir -p $out/share/reservoir
              cp -r manage.py web puzzles static $out/share/reservoir/
              ln -s ${virtualenv}/bin $out/bin
            '';
          };
        in
        {
          packages.default = app;
          packages.reservoir = app;

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
