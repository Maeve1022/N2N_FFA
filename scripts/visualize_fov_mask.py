from pathlib import Path
from collections import defaultdict
import random

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# ===== 1. 路径与随机种子 =====
project_root = Path(__file__).resolve().parents[1]
data_dir = project_root / "data" / "raw"
save_dir = project_root / "outputs" / "figures"
save_dir.mkdir(parents=True, exist_ok=True)

seed = 42
rng = random.Random(seed)

valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# ===== 2. 圆形有效视野 mask =====
def make_fov_mask(height=816, width=816,
                  center_x=408, center_y=408,
                  radius=385):
    yy, xx = np.ogrid[:height, :width]

    mask = (
        (xx - center_x) ** 2
        + (yy - center_y) ** 2
        <= radius ** 2
    )

    return mask


# ===== 3. 读取并做“候选预处理” =====
def load_for_preview(path):
    with Image.open(path) as img:
        # 无论原始高度是 816、840 或 861，先保留顶部 816×816
        img = img.crop((0, 0, 816, 816))

        # 统一显示为灰度图
        img = img.convert("L")

        image = np.asarray(img)

    return image


# ===== 4. 按原始尺寸分组 =====
image_paths = sorted(
    p for p in data_dir.iterdir()
    if p.is_file() and p.suffix.lower() in valid_ext
)

paths_by_size = defaultdict(list)

for path in image_paths:
    with Image.open(path) as img:
        paths_by_size[img.size].append(path)

target_sizes = [
    (816, 816),
    (816, 840),
    (816, 861),
]

for size in target_sizes:
    print(f"{size}: {len(paths_by_size[size])} 张")


# ===== 5. 每种尺寸随机抽两张：原图+mask结果 =====
mask = make_fov_mask()

fig, axes = plt.subplots(3, 4, figsize=(16, 12))

for row, size in enumerate(target_sizes):
    selected_paths = rng.sample(paths_by_size[size], k=2)

    for sample_index, path in enumerate(selected_paths):
        image = load_for_preview(path)
        masked_image = image.copy()
        masked_image[~mask] = 0

        # 左列：原图 + 红色圆形边界
        ax_original = axes[row, sample_index * 2]
        ax_original.imshow(image, cmap="gray", vmin=0, vmax=255)
        ax_original.contour(
            mask.astype(np.uint8),
            levels=[0.5],
            colors="red",
            linewidths=1
        )
        ax_original.set_title(
            f"原图：{size[0]}×{size[1]}\n{path.name[:28]}..."
        )
        ax_original.axis("off")

        # 右列：mask 后结果
        ax_masked = axes[row, sample_index * 2 + 1]
        ax_masked.imshow(masked_image, cmap="gray", vmin=0, vmax=255)
        ax_masked.set_title("应用圆形 FOV mask 后")
        ax_masked.axis("off")

plt.tight_layout()

save_path = save_dir / "fov_mask_preview.png"
plt.savefig(save_path, dpi=200)
plt.show()

print(f"\n预览图已保存至：{save_path}")