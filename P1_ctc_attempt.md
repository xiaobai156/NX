# P1 CTC training-state attempt

Attempted to construct the training model from the local PaddleOCR v3.7.0 vendor and `PP-OCRv6_medium_rec.yml` on `gpu:0`.

Result: stopped at model construction with `TypeError: MultiHead.__init__() missing 1 required positional argument: out_channels_list`. The raw YAML is not the complete runtime config; PaddleOCR's training setup derives output-channel mappings from the dictionary/postprocess configuration before calling `build_model`. No fallback or fake gradient test was used.

Status: BLOCKED pending the canonical PaddleOCR training launcher/config assembly. Existing inference forward checks remain valid.
# P1 CTC follow-up

`out_channels_list` was derived from the dictionary size (662 CTC, 665 NRTR), matching PaddleOCR's official train.py logic. The training model now constructs and reaches its training forward on `gpu:0`; the probe stopped because MultiHead requires encoded CTC/NRTR targets and the synthetic call supplied none. This is expected for the multi-head training contract, not a CUDA failure. Real dataset label encoding is required before loss/backward.
