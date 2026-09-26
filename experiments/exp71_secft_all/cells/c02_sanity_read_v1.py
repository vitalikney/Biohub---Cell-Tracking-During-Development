import numpy as np
import zarr

train_root = competition / "train"
sample = next(
    path for path in sorted(train_root.glob("*.zarr"))
    if path.with_suffix(".geff").exists()
)
dataset = trainer.open_dataset(
    sample, require_tracks=True, load_image=False, downsample=(1, 4, 4)
)
image = zarr.open_group(str(dataset.zarr_path), mode="r")["0"]
frame = np.asarray(image[0, :, ::4, ::4])
assert frame.ndim == 3 and frame.size > 0 and np.isfinite(frame).all()
print("读取成功:", sample.name, "图像:", frame.shape)
print("标注节点数:", len(dataset.tracks.node_attrs()))
