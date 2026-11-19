# Bundled third-party assets

The repository's MIT license covers its original code. The assets below retain
their upstream licenses and notices.

## Fonts — SIL Open Font License 1.1

| Family | Bundled location | License and copyright notice |
|---|---|---|
| Inter | `assets/inter-*.ttf`, `engine/fonts/Inter-Bold.ttf`, `engine/fonts/inter-Regular.ttf` | [inter-OFL.txt](inter-OFL.txt) |
| Space Grotesk | `assets/spacegrotesk-*.ttf` | [spacegrotesk-OFL.txt](spacegrotesk-OFL.txt) |
| Anton | `engine/fonts/Anton-Regular.ttf` | [anton-OFL.txt](anton-OFL.txt) |
| Playfair Display | `engine/fonts/PlayfairDisplay-Italic-var.ttf` | [playfairdisplay-OFL.txt](playfairdisplay-OFL.txt) |
| Caveat | `engine/fonts/caveat-latin-700-normal.woff2` | [caveat-OFL.txt](caveat-OFL.txt) |

License texts are copied from the corresponding `ofl/<family>/OFL.txt` files in
[Google Fonts](https://github.com/google/fonts/tree/main/ofl). Embedded font
copyright notices remain in the font files.

## Robust Video Matting

`models/rvm_mobilenetv3_fp32.onnx` is the MobileNetV3 FP32 model from
[Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting), by
Shanchuan Lin, Linjie Yang, Imran Saleemi and Soumyadip Sengupta.

- Upstream model: [v1.0.0 ONNX release](https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx).
- Source and training/inference documentation: [upstream repository](https://github.com/PeterL1n/RobustVideoMatting).
- ONNX exporter: [upstream ONNX branch](https://github.com/PeterL1n/RobustVideoMatting/tree/onnx).
- Upstream license: [GNU GPL v3](RVM-GPL-3.0.txt). The model is not relicensed under this repository's MIT license.

Python/npm dependencies and external services are installed or connected separately
and retain their own licenses and terms.
