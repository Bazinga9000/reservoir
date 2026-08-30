# ℝeservoir

A puzzlehunt management webapp used by ℙoNDeterministic.

## External Setup

### Google Integration (For per-puzzle Google Sheets)

1. Go to your (team's) Google account, and create a [Google Cloud Project](https://console.cloud.google.com/projectcreate)
2. Click "Enable APIs and Services" and enable the Google Sheets API and the Google Drive API
3. Under "Google Auth Platform" > "Clients", create a client. Set its type to "Desktop App". Download the credentials json and save it as `google_oauth.json`
4. Under "Google Auth Platform" > "Audience", add your (team's) Google email as a test user. 

5. Make a spreadsheet and format it however you'd like. This will be the sheet from which all puzzle sheets will be duplicated. Make sure the account used in step 4 has access to this sheet. Get its ID from the URL (`https://docs.google.com/spreadsheets/d/<ID_IS_HERE>/edit`). This is `SHEETS_TEMPLATE_ID`
 
6. In your (team's) Google Drive, create a new folder. This will be where your puzzle sheets get stored. Get its ID from the URL as you did in step 5. This is `SHEETS_FOLDER_ID`

7. Run `uv run authenticate_google.py` to authenticate the app with your (team's) Google account and generate (more) persistent credentials. This is done so that the end users don't have to authenticate randomly. This produces `google_authorized_user.json`. Note that this token eventually expires; when it does, re-run this step.

At the end of this section you should have two files:
- `google_oauth.json` — the OAuth client credentials
- `google_authorized_user.json` — the user token generated in step 7

and the following values:
- `TEAM_NAME` — your team name
- `SHEETS_TEMPLATE_ID` — the ID of your template sheet from step 5
- `SHEETS_FOLDER_ID` — the ID of the Google Drive folder from step 6

### Discord Integration (For authentication)

This site relies on Discord as an authentication provider. You will need to set up (or obtain credentials for) [a Discord application](https://discord.com/developers/docs/topics/oauth2).

1. Obtain the following two values for your Discord application:
   - the Client ID
   - the Client Secret. Note that clicking Reset Secret to view the secret will nullify any in-use secrets.
2. Determine the Redirect URL. 
   - This is usually where you will be hosting your server, with `/auth` appended. For debugging purposes this can be something like `http://localhost:8080/auth`.
3. Configure this URL as a valid Redirect URI for Discord OAuth.

At the end of this section you should have the following values:
- `DISCORD_CLIENT_ID` — the client ID
- `DISCORD_CLIENT_SECRET` — the client secret
- `DISCORD_REDIRECT_URI` — the redirect URI you entered into Discord

## Development

For easy development, you can use `process-compose`:

1. Install `uv`, `redis`, `process-compose`, and [`sajak_http`](https://github.com/Bazinga9000/sajak). (If you're using Nix/NixOS, just `nix develop` and pull them from the provided flake)
2. Provide the secrets and values from the external services setup:
   - Put `google_oauth.json` and `google_authorized_user.json` under `secrets/` in this repo's directory.
   - Create a `.env` file in this repo's directory with all the variables (`TEAM_NAME`, `SHEETS_TEMPLATE_ID`, `SHEETS_FOLDER_ID`, `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`).
3. Run `process-compose` in this directory.

## Deployment (NixOS)

The flake provides a package and a NixOS module for deploying reservoir as a
systemd service. The service runs the app with daphne, a redis instance for the channel layer, and optionally
[`sajak_http`](https://github.com/Bazinga9000/sajak) for the `/sajak` chat
command.

### Secrets

Secrets are provided to the service as file paths, so they can be managed with
[agenix](https://github.com/ryantm/agenix) or [sops-nix](https://github.com/Mic92/sops-nix) (or plain files on disk if you
don't care, but note these will be world-readable in the Nix store). Three files are expected:

1. A dotenv file containing all the variables from the external services
   setup (`TEAM_NAME`, `SHEETS_TEMPLATE_ID`, `SHEETS_FOLDER_ID`,
   `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`).
2. The Google OAuth client credentials (`google_oauth.json`).
3. The Google authorized user token (`google_authorized_user.json`)

### Module options

The module is exposed as `nixosModules.default` in this flake. The important options:

- `services.reservoir.enable` — turn the service on.
- `services.reservoir.dotenvFile` — path to the dotenv file (1 above).
- `services.reservoir.googleOauthCredentials` — path to the Google OAuth client credentials (2 above).
- `services.reservoir.googleAuthorizedUser` — path to the Google authorized user token (3 above).
- `services.reservoir.port` / `services.reservoir.bindAddress` — what to
  listen on (default `127.0.0.1:8000`; put a reverse proxy in front for TLS).
- `services.reservoir.whitenoise.enable` — serve static files from the app
  itself via [whitenoise](https://whitenoise.readthedocs.io/) (default `true`). 
  - Keep this on if you want a self-contained deployment.
  - If you prefer the conventional setup, disable this and have your reverse proxy serve `/static/` from `/var/lib/reservoir/static` (populated by `collectstatic` on service start), proxying everything else to the app.
- `services.reservoir.sajak.enable` — also run `sajak_http` (default `true`). The app hardcodes `localhost:1983` for sajak, so only disable this if you're running sajak elsewhere on that port.

The sqlite database and static files live under `/var/lib/reservoir` (configurable via `services.reservoir.stateDir`). Migrations run automatically before the service starts.

### Example configuration

```nix
{
  inputs.reservoir.url = "github:Bazinga9000/reservoir";

  outputs = { self, nixpkgs, reservoir, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        reservoir.nixosModules.default
        {
          services.reservoir = {
            enable = true;
            port = 8080;
            # see agenix's repo for how to properly configure this
            dotenvFile = config.age.secrets.reservoir-env.path;
            googleOauthCredentials = config.age.secrets.google-oauth.path;
            googleAuthorizedUser = config.age.secrets.google-authorized-user.path;
          };
        }
      ];
    };
  };
}
```
