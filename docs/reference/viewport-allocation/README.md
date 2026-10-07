# Native viewport and UI-density allocation diagnostic

Three fresh Godot 4.7.2 Compatibility processes used the current `90c4f70e…` source on the Apple M2 Max. Each visited stationary cell/gate/pavilion cameras, then opened the local reading and finale. These are allocation probes, not collision traversal or frame-time measurements.

| State | 1410 × 600, scale 1 | 1080 × 1984, scale 1 | 1080 × 1984, scale 2.625 | Density-only increase |
| --- | ---: | ---: | ---: | ---: |
| Cell | 49,632,517 B | 66,920,701 B | 68,056,659 B | 1,135,958 B |
| Gate | 49,763,589 B | 67,051,773 B | 68,580,947 B | 1,529,174 B |
| Pavilion | 49,719,899 B | 67,008,083 B | 68,585,039 B | 1,576,956 B |
| Reading | 50,025,733 B | 67,313,917 B | 69,808,377 B | 2,494,460 B |
| Finale | 50,200,495 B | 67,488,679 B | 71,905,529 B | 4,416,850 B |

Changing only the native window size adds 17,288,184 bytes (16.49 MiB) in every state. Every run retains the same 88 scene texture RIDs, paths, dimensions, formats and calculated stored mip cost of 36,505,432 bytes. Readback leaves renderer allocation unchanged.

The requested portrait window was 1080 × 2340, but macOS clamped it to 1080 × 1984. The direct RenderingServer image readback records that actual size; the current Pixel images are 1080 × 2340. This diagnostic cannot be subtracted from the phone as an exact same-size platform comparison. At UI scale 2.625, ViewportTexture metadata says 2835 × 5208 while the actual image remains 1080 × 1984. Metadata alone is not a physical framebuffer-size measurement.

The reachable theme-font CPU image totals are unchanged between densities: 393,216 bytes at the arrivals, 524,288 at reading and 655,360 at finale. Those partial caches therefore do not explain the density-dependent renderer increments. They omit other font caches and are not complete GPU storage measurements. No font-size or oversampling reduction was installed.

The [versioned Godot Compatibility source](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/storage/utilities.cpp#L410) returns tracked texture plus render-buffer bytes for `RENDERING_INFO_TEXTURE_MEM_USED`. It is broader than the scene Texture2D inventory. Native-window-dependent allocations need to be included in the budget; a small texture inventory alone cannot establish acceptance. The named counter remains the measured acceptance metric in this project.

`desktop.json`, `phone-size.json` and `phone-density.json` retain full inventories and metadata. The matching native logs are clean. `installed-api.log` records the installed texture/font/viewport diagnostic methods. `export/viewport-allocation-diagnosis.json` verifies their hashes and comparisons. No production scene, source texture, camera, UI scaling or rendering resolution changed. Actual Android allocation attribution and budget acceptance remain open.

Run one fresh native process per case:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path godot \
  --script res://tests/profile_viewport_allocation.gd -- \
  --width=1080 --height=2340 --ui-dpi=420 --output=/tmp/garden-density.json
```
