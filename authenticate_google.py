# The only reason this script exists is to generate the authorized user JSON without having to do anything on the actual webserver.
# Just `uv run authenticate_google` and login with its URL. Then, the server will be able to use the generated token without your input
# until it expires and you'll have to do it again. This is easier and less error prone then exposing the google authentication to the end users.

import puzzles.google

print("Authenticating. If nothing happens after this, you already have non-expired OAuth credentials.")
puzzles.google.get_client()
print("Done.")