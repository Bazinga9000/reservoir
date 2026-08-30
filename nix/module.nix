{
  app,
  sajakModule,
}:
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.services.reservoir;

  # The dotenv file is passed as a path so agenix secrets work out of the box.
  # The Google secrets are likewise passed as paths and wired into the app via
  # environment variables (see puzzles/google.py).
  dotenvFile = cfg.dotenvFile;
in
{
  options.services.reservoir = {
    enable = lib.mkEnableOption "reservoir puzzlehunt webapp";

    package = lib.mkOption {
      type = lib.types.package;
      default = app;
      description = "The reservoir package to use.";
    };

    port = lib.mkOption {
      type = lib.types.port;
      default = 8000;
      description = "Port for the web server to listen on.";
    };

    bindAddress = lib.mkOption {
      type = lib.types.str;
      default = "127.0.0.1";
      description = "Address for the web server to bind to.";
    };

    workers = lib.mkOption {
      type = lib.types.int;
      default = 2;
      description = "Reserved for future use; daphne is single-process async.";
    };

    stateDir = lib.mkOption {
      type = lib.types.path;
      default = "/var/lib/reservoir";
      description = "Directory for the sqlite database and other state.";
    };

    whitenoise = {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = ''
          Serve static files from the app itself using whitenoise, making the
          deployment self-contained (no reverse proxy needed for /static/).
          Disable this if you serve static files with your own reverse proxy
          (e.g. nginx) pointing at the STATIC_ROOT directory.
        '';
      };
    };

    # Secrets, given as file paths so agenix can be used.
    dotenvFile = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      example = lib.literalExpression "config.age.secrets.reservoir-env.path";
      description = ''
        Path to a dotenv file containing TEAM_NAME, SHEETS_TEMPLATE_ID,
        SHEETS_FOLDER_ID, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET and
        DISCORD_REDIRECT_URI. Intended to be used with agenix.
      '';
    };

    googleOauthCredentials = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      example = lib.literalExpression "config.age.secrets.google-oauth.path";
      description = ''
        Path to the Google OAuth client credentials JSON
        (secrets/google_oauth.json in the dev setup).
      '';
    };

    googleAuthorizedUser = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      example = lib.literalExpression "config.age.secrets.google-authorized-user.path";
      description = ''
        Path to the Google authorized user JSON
        (secrets/google_authorized_user.json in the dev setup).
      '';
    };

    sajak = {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = "Whether to enable the sajak-http service (used by the /sajak chat command).";
      };
      port = lib.mkOption {
        type = lib.types.port;
        default = 1983;
        description = "Port for sajak-http. The app hardcodes localhost:1983.";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    services.sajak-http = lib.mkIf cfg.sajak.enable {
      enable = true;
      port = cfg.sajak.port;
    };

    services.redis.servers.reservoir = {
      enable = true;
      port = 6379;
    };

    users.users.reservoir = {
      isSystemUser = true;
      group = "reservoir";
    };
    users.groups.reservoir = { };

    systemd.services.reservoir = {
      description = "reservoir puzzlehunt webapp";
      after = [
        "network.target"
        "redis-reservoir.service"
      ] ++ lib.optionals cfg.sajak.enable [ "sajak-http.service" ];
      wants = [ "redis-reservoir.service" ] ++ lib.optionals cfg.sajak.enable [ "sajak-http.service" ];
      wantedBy = [ "multi-user.target" ];

      environment = {
        DJANGO_SETTINGS_MODULE = "web.settings";
        RESERVOIR_DOTENV = lib.mkIf (dotenvFile != null) (toString dotenvFile);
        GOOGLE_OAUTH_CREDENTIALS = lib.mkIf (cfg.googleOauthCredentials != null) (
          toString cfg.googleOauthCredentials
        );
        GOOGLE_AUTHORIZED_USER = lib.mkIf (cfg.googleAuthorizedUser != null) (
          toString cfg.googleAuthorizedUser
        );
      };

      preStart = ''
        cd ${cfg.package}/share/reservoir
        ${cfg.package}/bin/python manage.py migrate --noinput
        ${cfg.package}/bin/python manage.py collectstatic --noinput --clear
      '';

      script = ''
        cd ${cfg.package}/share/reservoir
        exec ${cfg.package}/bin/daphne \
          --bind ${cfg.bindAddress} \
          --port ${toString cfg.port} \
          web.asgi:application
      '';

      serviceConfig = {
        Type = "exec";
        User = "reservoir";
        Group = "reservoir";
        StateDirectory = "reservoir";
        WorkingDirectory = "${cfg.package}/share/reservoir";
        Restart = "on-failure";
        # The sqlite db lives in the state dir; point Django at it.
        Environment = [
          "RESERVOIR_DB_PATH=${cfg.stateDir}/db.sqlite3"
          "RESERVOIR_STATIC_ROOT=${cfg.stateDir}/static"
        ] ++ lib.optionals cfg.whitenoise.enable [ "RESERVOIR_WHITENOISE=1" ];
        ReadWritePaths = [ cfg.stateDir ];
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
      };
    };
  };
}