from pathlib import Path
from collections import Counter
import re

from PIL import Image


# ===== 1. 项目与数据路径 =====
project_root = Path(__file__).resolve().parents[1]
data_dir = project_root / "data" / "raw"

valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# ===== 2. 获取全部图像文件 =====
image_paths = sorted(
    p for p in data_dir.iterdir()
    if p.is_file() and p.suffix.lower() in valid_ext
)

print(f"原始图像总数：{len(image_paths)}")


# ===== 3. 按文件名结尾识别视野角度 =====
def get_view_angle(path):
    """
    例如：
    xxx_FFA_OD_45°.jpg  -> "45°"
    xxx_FFA_OS_135°.png -> "135°"
    """
    match = re.search(r"_(45|135)°$", path.stem)

    if match is None:
        return "unknown"

    return f"{match.group(1)}°"


# ===== 4. 统计图像数量与尺寸 =====
paths_by_angle = {
    "45°": [],
    "135°": [],
    "unknown": []
}

size_by_angle = {
    "45°": Counter(),
    "135°": Counter(),
    "unknown": Counter()
}

read_errors = []

for path in image_paths:
    angle = get_view_angle(path)

    try:
        with Image.open(path) as img:
            img.load()

            paths_by_angle[angle].append(path)
            size_by_angle[angle][img.size] += 1

    except Exception as e:
        read_errors.append((path.name, str(e)))


# ===== 5. 输出统计结果 =====
print("\n" + "=" * 50)
print("视野角度统计")
print("=" * 50)

for angle in ["45°", "135°", "unknown"]:
    print(f"\n{angle} 图像数量：{len(paths_by_angle[angle])} 张")
    print(f"{angle} 图像尺寸分布：")

    if len(size_by_angle[angle]) == 0:
        print("  无")
        continue

    for size, count in sorted(
        size_by_angle[angle].items(),
        key=lambda item: item[1],
        reverse=True
    ):
        width, height = size
        print(f"  {width} × {height}: {count} 张")


# ===== 6. 输出未识别文件示例 =====
if paths_by_angle["unknown"]:
    print("\n" + "=" * 50)
    print("无法根据文件名识别角度的前 10 张图：")
    print("=" * 50)

    for path in paths_by_angle["unknown"][:10]:
        print(path.name)


# ===== 7. 输出读取失败信息 =====
print("\n" + "=" * 50)
print(f"读取失败图像：{len(read_errors)} 张")
print("=" * 50)

for name, error in read_errors[:10]:
    print(f"{name} -> {error}")