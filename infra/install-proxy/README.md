# Install Proxy

Deploy this folder as a dedicated Cloudflare Worker and attach the `install.opensre.com` domain.

Suggested setup:

1. Make sure the `opensre.com` zone is active in Cloudflare.
2. From `infra/install-proxy`, authenticate with Cloudflare:
   `npx wrangler login`
3. Deploy the Worker:
   `npx wrangler deploy`
4. Confirm the custom domain route for `install.opensre.com` from `wrangler.jsonc`, or add it in the Cloudflare dashboard if you prefer dashboard-managed routing.

After the domain is live, the single public installer entrypoint is:

- `https://install.opensre.com`

Examples:

- `curl -fsSL https://install.opensre.com | bash`
- `curl -fsSL https://install.opensre.com | bash -s -- --main`
- `irm https://install.opensre.com | iex`

The root URL auto-detects `curl`/Unix versus PowerShell and serves the right installer script body.

If you ever need to force shell detection manually, append:

- `?shell=sh`
- `?shell=powershell`
