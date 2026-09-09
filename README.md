# Business OCR Train

Windows PySide6 UI preview for the closed-business OCR training workflow.

## Status

Version 0.1.3 is a UI preview: directory selection, GPU visibility check, and read-only image/TXT counting. Training, full TXT parsing, GPU localization, and model export are not implemented yet.

Build with `powershell -ExecutionPolicy Bypass -File .\build_exe.ps1`.

The `已分流` marker is removed as a status marker while retaining the record; it does not cause the whole record to be skipped.

## Delivery rule

After each change, run the relevant verification before committing and pushing. Never commit source images, truth TXT, caches, `build/`, or `dist/` output.
