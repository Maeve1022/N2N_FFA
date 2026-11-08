from pathlib import Path

data_dir = Path(r"D:\PyTorch\N2N_FFA\data\raw")

valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

image_paths = sorted(
    p for p in data_dir.iterdir()
    if p.is_file() and p.suffix.lower() in valid_ext
)

print(f"图像总数：{len(image_paths)}")

from PIL import Image
import numpy as np
from collections import Counter

size_counts = Counter()
mode_counts = Counter()
dtype_counts = Counter()

all_mins = []
all_maxs = []
all_means = []
errors = []

for i, path in enumerate(image_paths, start=1):
    try:
        with Image.open(path) as img:
            img.load()  # 真正读取，损坏文件会在这里报错
            arr = np.asarray(img)

            height, width = arr.shape[:2]

            size_counts[(width, height)] += 1
            mode_counts[img.mode] += 1
            dtype_counts[str(arr.dtype)] += 1

            all_mins.append(arr.min())
            all_maxs.append(arr.max())
            all_means.append(arr.mean())

    except Exception as e:
        errors.append((path.name, str(e)))

print("\n--- 图像尺寸统计（前 10 项）---")
for size, count in size_counts.most_common(10):
    print(f"{size}: {count} 张")

print("\n--- 图像模式统计 ---")
print(mode_counts)

print("\n--- 数据类型统计 ---")
print(dtype_counts)

print("\n--- 像素统计 ---")
print(f"所有图像最小像素值：{min(all_mins)}")
print(f"所有图像最大像素值：{max(all_maxs)}")
print(f"单张图平均亮度范围：{min(all_means):.2f} ~ {max(all_means):.2f}")

print("\n--- 读取失败图像 ---")
print(f"数量：{len(errors)}")
for name, message in errors[:10]:
    print(name, "->", message)