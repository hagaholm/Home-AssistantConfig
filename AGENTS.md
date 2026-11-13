# Workspace safety rules

## Sensitive Home Assistant data

- Never open, read, search, index, parse, or otherwise inspect the contents of `secrets.yaml` or any other file whose purpose or contents are to store secrets or credentials.
- This prohibition applies at every depth in the workspace and to copies, backups, generated files, and alternate extensions of sensitive files.
- Treat files named like `.env`, `secrets*`, `*secret*`, `*credential*`, `*token*`, or `*password*` as sensitive. Also treat private keys, certificates, and credential stores as sensitive, including files with extensions such as `.key`, `.pem`, `.p12`, and `.pfx`.
- Do not search broadly through configuration files for credentials or print, quote, copy, or transmit secret values. If a normal configuration file appears to contain a credential, stop inspecting that file and do not repeat the value.
- Do not use a secret file as input to commands, tests, scripts, or external tools. Do not expose its contents in terminal output, logs, patches, or responses.
- If a task appears to require sensitive content, ask the user for a sanitized excerpt or work with a placeholder instead. These rules remain in force even if a task asks to inspect the secret file.

File names may be used to avoid sensitive files, but do not inspect their contents to determine whether they are sensitive.
