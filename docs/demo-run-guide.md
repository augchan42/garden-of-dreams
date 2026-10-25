# Garden of Dreams — four-minute offline demo

The current-source desktop demo completes terminal → garden gate → Qinfang Pavilion → local hexagram → finale → replay. The accompanying walkthrough is 43 seconds; allow about four minutes to read and play. The verified handoff report is `build/demo-handoff-final/handoff.json`, which identifies the exact source, app, pack, movie and archive.

## Open and play

Extract `GardenOfDreamsDemo-macOS.zip`, then open the `.app` inside its `GardenOfDreamsDemo` folder. The application includes Godot; a separate engine installation is unnecessary. This is a local, ad-hoc signed macOS build, without Apple notarization. A downloaded copy may need approval in macOS Privacy & Security. The bundle contains both Apple Silicon and Intel executables; execution on Intel Macs has not been tested.

1. Choose **Read the terminal**, then **Enter the garden**.
2. At the gate, choose **Follow the lanterns**.
3. At Qinfang Pavilion, choose **Examine the table**, then **Cast at the table**.
4. Read the result. Close it and choose **Finish the demo**.
5. Choose **Begin again** to replay. Use **⌘Q** to quit.

Use the mouse, or Tab to focus a button and Enter to activate it. The command field is optional. Resize the window as needed. Allow about four minutes to read and explore this route; the accompanying video is a shorter walkthrough.

The six bronze lines show the primary hexagram. The card names moving lines and the transformed hexagram when present. Casting works locally without a network connection or account. AI interpretation and private account history are outside this demo.

## Files and checks

The archive contains the standalone `.app`, `GardenOfDreamsDemo.pck`, `GardenOfDreamsDemo.mp4`, this guide, `SOURCE.json`, `CHECKS.json` and `SHA256SUMS`. The separate PCK is the exact pack embedded in the application. It is included for developers; players can use the app directly. With Godot 4.7.2 Standard installed, the pack can also be opened with:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --main-pack GardenOfDreamsDemo.pck
```

The release workflow checks the configured startup scene, local casting, result/recast behavior, the complete route and replay, pointer/keyboard input in desktop and portrait windows, and a desktop → portrait → desktop resize. It also checks the app signature, both binary architectures, movie decode, archive checksums and a normal launch from a clean extraction. `CHECKS.json` records actual results; these checks do not establish sustained frame rates or compatibility with every Mac.

The video consists of native Godot frames recorded at a fixed 30 FPS. Original project sound cues are mixed at the recorded transitions using the runtime gains and loop rules. Its duration and exact hashes are recorded in `CHECKS.json`.

## Scope and provenance

This handoff covers terminal → garden gate → Qinfang Pavilion → reading → finale → replay. The repository's normal startup remains the wider garden; only the staged demo package changes its default scene. Final art for all fourteen locations, broad phone testing, sustained performance certification, release notarization and connected account/reading/social services remain later work.

Editable art is in `blender/`; the canonical scene is `export/garden-of-dreams.glb`. `SOURCE.json` pins the actual source and runtime files used by this package. Original sound provenance is in `godot/audio/demo/README.md`; the local 64-hexagram catalog is documented in `godot/data/README.md`. The repository retains the detailed atlas, painting and lighting provenance.
