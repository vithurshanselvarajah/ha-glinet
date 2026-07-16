# SSL Certificate Verification

The integration skips TLS certificate verification of your GL.iNet router on
every connection. Verification is **off by default** because most GL.iNet
routers ship with a self-signed certificate that fails strict validation.

## When to enable it

Enable **Verify SSL Certificate** in the config or options form if your
router uses a trusted certificate — for example, one issued by a private CA
on your network or by a public CA such as Let's Encrypt.

## What it does

- **Disabled (default)** — Certificate validation is skipped. Any TLS
  certificate is accepted, including the stock GL.iNet self-signed certificate.
  This is functionally equivalent to clicking through a browser's "your
  connection is not private" warning. The setting only affects traffic to
  your own router on your local network.
- **Enabled** — HTTPS requests validate the certificate against the system
  trust store. Self-signed, expired, or mismatched certificates cause the
  connection to fail.

## Changing the setting

1. **Settings → Devices & Services → GL.iNet Router → Configure**.
2. Toggle **Verify SSL Certificate**.
3. Submit. The options form re-runs the connection test and full login before
   saving, so a broken setting will surface as a `cannot_connect` error
   instead of being persisted.
