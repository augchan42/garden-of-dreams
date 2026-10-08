# Shaw Brothers trailer lighting references

Eight distinct decoded frames fill eight generic night-set reference slots. Each frame was directly reviewed at its original decoded size. Three downloaded distributor video streams are retained byte for byte; exact commands, first selected stream PTS, extracted PNG hashes and FFmpeg logs are recorded in `selected-frame-provenance.json`. These references are outside the shipped Godot assets. No crop, resize or added color grade was applied to the saved frames; publisher framing, bars and subtitles remain.

The sources are [Arrow Video's Come Drink With Me trailer](https://www.youtube.com/watch?v=astCEpTZTiw), [Shaw Brothers Clips' Magic Blade trailer](https://www.youtube.com/watch?v=FU-5zusTJSY) and [Shaw Brothers Clips' Enchanting Shadow trailer](https://www.youtube.com/watch?v=oJ_Sy5j1XYU). Publisher metadata preserves titles, channels, upload dates and descriptions, together with the raw downloaded metadata hash. Temporary streaming URLs and format lists are omitted. The stream filenames are local archive names, not publisher titles.

[Celestial Pictures' company page](https://www.celestialpictures.com/company.php) describes its ownership of the Shaw film library. Its original HTML snapshot and hash are retained. Ownership/public trailer availability does not grant an open licence; no redistribution permission is asserted. Individual frame photographers and capture dates are uncredited. Reference collection does not authorize shipping these frames as textures or artwork.

The Enchanting Shadow trailer labels the film 1959. The [Hong Kong Film Archive record](https://www.filmarchive.gov.hk/en/web/hkfa/pe-event-2017-9-1-7.html), already saved in the Qiushuang reference folder, gives 1960 and Celestial copyright attribution. Both source statements are retained; the channel year is not treated as verified. The 600 × 480 Shaw trailer streams support broad layout/light/material contrast, not fine joinery or measured color values.

The selected frames distinguish warm wood and lamps, cream/gray stone or plaster, restricted blue foliage/background light and dark unlit areas. This is guidance for the user's less-green revision, not a copied grade, a measured light setup or final scene acceptance. The selected films do not identify any named garden site.

Rejected sample images and reasons are retained separately in `rejected-samples.json`. The sampled Come Drink With Me stone bridge does not establish the required bridge pavilion; a 36th Chamber training-vat crop does not establish a cell; Magic Blade stone ground does not establish a cave corridor; an Enchanting Shadow writing-table crop does not establish Hengwu night-exterior lighting. These slots remain open. The sample windows are approximate, while accepted-frame PTS values are exact decoder observations.

| Site | Slot | Film | Trailer PTS (s) |
| --- | --- | --- | --- |
| [daoxiang-cun](../../daoxiang-cun/README.md) | 1 | Come Drink With Me | 24.607917 |
| [aojing-guan](../../aojing-guan/README.md) | 1 | The Magic Blade | 5.0 |
| [longcui-an](../../longcui-an/README.md) | 1 | The Magic Blade | 3.0 |
| [qinfang-ting](../../qinfang-ting/README.md) | 2 | The Magic Blade | 53.0 |
| [ouxiang-xie](../../ouxiang-xie/README.md) | 1 | The Enchanting Shadow | 15.0 |
| [daguan-lou](../../daguan-lou/README.md) | 1 | The Enchanting Shadow | 17.0 |
| [tubi-tang](../../tubi-tang/README.md) | 1 | The Enchanting Shadow | 3.0 |
| [ziling-zhou](../../ziling-zhou/README.md) | 1 | The Enchanting Shadow | 11.0 |
