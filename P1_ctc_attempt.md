# P1 CTC training-state attempt

Attempted to construct the training model from the local PaddleOCR v3.7.0 vendor and `PP-OCRv6_medium_rec.yml` on `gpu:0`.

Result: stopped at model construction with `TypeError: MultiHead.__init__() missing 1 required positional argument: out_channels_list`. The raw YAML is not the complete runtime config; PaddleOCR's training setup derives output-channel mappings from the dictionary/postprocess configuration before calling `build_model`. No fallback or fake gradient test was used.

Status: BLOCKED pending the canonical PaddleOCR training launcher/config assembly. Existing inference forward checks remain valid.
