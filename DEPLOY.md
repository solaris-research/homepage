# Deployment playbook — solaris-research.com

This is a one-time setup to get the site live at `solaris-research.com` via GitHub Pages, with DNS pointed from GoDaddy.

Total time: ~20 minutes of clicks + 10–60 minutes of DNS propagation.

---

## Step 1 — Create the GitHub repo

The repo **must** be named `solaris-research.github.io` (this is the convention GitHub requires for org-level Pages sites served at the org root).

1. Go to <https://github.com/organizations/solaris-research/repositories/new>.
2. Repository name: `solaris-research.github.io`
3. Description: *Source for solaris-research.com — Solaris Research landing page*
4. **Public** (required for free GitHub Pages on personal/org accounts).
5. Do **not** add a README, .gitignore, or license — we already have them locally.
6. Click **Create repository**.

---

## Step 2 — Push the site

From your local copy of this folder:

```bash
cd /path/to/solaris-research
git init -b main
git add .
git commit -m "Initial commit: Solaris Research landing page"
git remote add origin git@github.com:solaris-research/solaris-research.github.io.git
git push -u origin main
```

If you haven't set up SSH for GitHub, use the HTTPS URL instead:
`https://github.com/solaris-research/solaris-research.github.io.git`.

---

## Step 3 — Enable GitHub Pages

1. Go to <https://github.com/solaris-research/solaris-research.github.io/settings/pages>.
2. **Source**: Deploy from a branch.
3. **Branch**: `main` / `/ (root)` → Save.
4. **Custom domain**: enter `solaris-research.com` → Save.
   - GitHub will show "DNS check in progress". This is expected until Step 4 is done.
5. **Enforce HTTPS**: leave this unchecked for now; tick it only after the DNS checks pass (otherwise the certificate provisioning fails).

---

## Step 4 — Configure DNS at GoDaddy

Log in to GoDaddy → My Products → `solaris-research.com` → **DNS**.

### 4a. Delete defaults you don't need

If GoDaddy has auto-added parking/forwarding records, remove them:
- Any `A` record at `@` pointing to GoDaddy parking
- The `CNAME` at `www` pointing to `@` (we'll replace it)
- The default `forwarding` rule (disable Domain Forwarding under Settings if enabled)

### 4b. Add these records

| Type  | Name | Value                    | TTL    |
|-------|------|--------------------------|--------|
| A     | @    | 185.199.108.153          | 1 Hour |
| A     | @    | 185.199.109.153          | 1 Hour |
| A     | @    | 185.199.110.153          | 1 Hour |
| A     | @    | 185.199.111.153          | 1 Hour |
| CNAME | www  | solaris-research.github.io. | 1 Hour |

(These four A records are GitHub Pages' anycast IPs. Source: <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site>.)

Optionally also add an `AAAA` set (IPv6) for faster resolution on IPv6 clients:

| Type | Name | Value                       | TTL    |
|------|------|-----------------------------|--------|
| AAAA | @    | 2606:50c0:8000::153         | 1 Hour |
| AAAA | @    | 2606:50c0:8001::153         | 1 Hour |
| AAAA | @    | 2606:50c0:8002::153         | 1 Hour |
| AAAA | @    | 2606:50c0:8003::153         | 1 Hour |

Save.

---

## Step 5 — Wait for DNS + verify

1. From your terminal:
   ```bash
   dig solaris-research.com +short
   # should return the four 185.199.x.153 IPs
   dig www.solaris-research.com +short
   # should return solaris-research.github.io. then the four IPs
   ```
2. On the GitHub Pages settings page, you should see a green check next to **DNS check successful**.
3. Now tick **Enforce HTTPS**. GitHub will provision a Let's Encrypt cert for both apex and www within a few minutes.
4. Visit <https://solaris-research.com> — you should see the landing page.

---

## Step 6 — Verify GitHub treats it as a Pages deployment

In your repo, the **Actions** tab should show a `pages-build-deployment` run after each push to `main`. If it's green, you're good.

---

## Troubleshooting

- **"Domain's DNS record could not be retrieved" on GitHub Pages settings**
  DNS hasn't propagated yet. Wait 15–60 minutes and re-check. Do not tick "Enforce HTTPS" until this clears.

- **Site loads on `solaris-research.github.io` but not on `solaris-research.com`**
  Most likely the `CNAME` file at the root of the repo is missing or has a typo. It should contain exactly:
  ```
  solaris-research.com
  ```
  (One line, no scheme, no trailing slash.)

- **`www` doesn't redirect to apex**
  Confirm the `CNAME www → solaris-research.github.io.` record. GitHub automatically serves the apex version as canonical once both resolve.

- **Cert provisioning stuck**
  Untick "Enforce HTTPS", wait 5 minutes, re-tick. If still stuck, remove the custom domain in GitHub settings, wait 10 minutes, and re-add it.

- **Mixed-content warnings**
  Everything on the site should use `https://` (or protocol-relative `//`). Grep for `http://` in the repo to double-check.
