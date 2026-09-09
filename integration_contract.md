# Formal OCR integration contract (P0 evidence)

- Project: `C:\Users\Administrator\Desktop\每天工具\N卡本地识别\OcrLineTool.App\OcrLineTool.App.csproj`
- Primary local entry: `PaddleLocalOcrClient.RecognizeBatchAsync(...)` and `RecognizeAsync(...)`.
- UI callers: `MainForm.cs` handlers `RecognizeLocalPrimaryAsync` and the primary recognition flow.
- Process boundary: the C# app starts packaged `运行组件\paddle_local_ocr.py`; model files are copied from `模型\**` by the project file.
- Return contract: local client returns a dictionary keyed by image path with lists of recognized strings; generic `IOcrClient.RecognizeAsync` returns a list of strings.
- Cache: local client uses `paddle-v6-cuda-cache.json`; this is existing production behavior and must be audited before reuse in the training runtime.
- Error behavior: `OcrException` and `IsCudaUnavailable(...)` are present; callers currently handle CUDA-unavailable errors. The new training runtime must enforce stop-on-CUDA-error and must not add CPU fallback.
- Existing app has cloud/fallback OCR paths in `MainForm.cs`; these are not acceptable as the new training runtime's hidden fallback and must remain outside the new engine contract.
- Inputs observed: image paths/batches, model/runtime configuration, max-side/detection settings. The training engine must additionally receive group/material/issue/field request without truth answer values.
- Outputs observed: recognized text lines and image-path association. The new formal adapter must add requested issue, material/field identity, status, confidence and source coordinates after the locator is implemented.

## TXT formats observed

Source: `新澳六合彩资料_251期.txt` (UTF-8, 251 issue).

- `【头】`: one or more number+`头` tokens, then material name; remove only trailing `（已分流）`.
- `【尾】`: one or more number+`尾` tokens, then material name; same marker rule.
- `【一肖】`: one zodiac token, then material name; same marker rule.
- `【二肖】`: two zodiac tokens, then material name; same marker rule.
- `【五行】`: one element token, then material name; same marker rule.
- `【5个数字】`: comma-separated zero-padded numeric string, then material name; preserve order, duplicates and leading zeros.
- `【5个以上数字】`: comma-separated numeric string of variable length, then material name; preserve order and leading zeros.
- `【30个以上数字】`: comma-separated numeric string of variable length, then material name; preserve order and leading zeros.
- `【段】`: number+`段` token, then material name; same marker rule.
- `缺失（未找到对应图片）` and `缺失（未识别到当期目标数据）`: skip sample creation, retain audit record.
- Unknown syntax must remain unparsed; do not guess.

## Status

P0 data and interface evidence is complete for the currently available files. Full production integration remains unverified until the formal adapter is implemented and tested against real end-to-end requests.
