# Security Policy / 安全说明

This project operates on **local media and optionally local Windows shortcuts**. It should not require administrator privileges, cloud credentials, API tokens or changes to the installed Codex package.

- Never upload video of real private conversations, private identifiers or account secrets in public issues.
- Do not download and run scripts from unfamiliar forks without reviewing them.
- The PowerShell shortcut wrapper may invoke `-ExecutionPolicy Bypass` **for that one subprocess only** to execute the locally reviewed helper; it is not a permanent system policy change. Review before use.
- The default mode creates a **new independent shortcut**; only the explicit `-ReplaceOriginal` option replaces an existing `.lnk`, with a timestamped backup.
- If you find a security issue, contact the repository maintainer privately through GitHub's private vulnerability reporting if enabled, or use an alternate private contact method. Do **not** post exploit details or secrets in a public issue.

中文版：不要在公开 Issue 中上传敏感录屏或密钥。请先审查脚本，默认只新建快捷方式；替换现有快捷方式需显式指定且有备份。发现安全问题请优先私下报告。
