import hashlib
import json
import pathlib
import shutil
import struct

ROOT = pathlib.Path('/Users/auchan/projects/garden-of-dreams')
FIRST = pathlib.Path(json.load(open('/tmp/garden-official-trailer-reference.json'))['folder'])
NIGHT = pathlib.Path(json.load(open('/tmp/garden-official-night-trailer-reference.json'))['folder'])
SUPPORT = ROOT / 'docs/reference/external/supporting/shaw-trailers'
SUPPORT.mkdir(parents=True, exist_ok=False)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def copy_exact(source, destination, expected=None):
    original = digest(source)
    assert expected is None or original == expected, str(source)
    assert not destination.exists(), str(destination)
    shutil.copyfile(source, destination)
    assert digest(destination) == original
    return original

trailers = {}
for folder, name, film in [(FIRST, 'come-drink', 'Come Drink With Me'),
                           (NIGHT, 'magic-blade', 'The Magic Blade'),
                           (NIGHT, 'enchanting-shadow', 'The Enchanting Shadow')]:
    report = json.load(open(folder / 'report.json'))
    item = next(x for x in report['items'] if x['name'] == name)
    metadata_path = folder / (name + '-metadata.json')
    assert digest(metadata_path) == item['metadata_sha256']
    raw = json.load(open(metadata_path))
    video = SUPPORT / (name + '.mp4')
    copy_exact(pathlib.Path(item['path']), video, item['sha256'])
    metadata = {k: raw.get(k) for k in ('id', 'title', 'channel', 'channel_url', 'uploader',
                                       'upload_date', 'duration', 'description')}
    metadata.update(film=film, source_page=item['source_page'],
                    saved_video=str(video.relative_to(ROOT)),
                    saved_video_sha256=digest(video), saved_video_bytes=video.stat().st_size,
                    raw_metadata_sha256=item['metadata_sha256'],
                    metadata_scope='Stable publisher fields from the downloaded metadata. Temporary stream URLs and format lists are omitted. Full downloaded video bytes are retained.',
                    metadata_command=item['metadata_command'],
                    download_command=item['download_command'],
                    metadata_exit_code=item['metadata_exit_code'],
                    download_exit_code=item['download_exit_code'])
    if name == 'enchanting-shadow':
        metadata['year_discrepancy'] = {
            'channel_title_and_description_year': 1959,
            'hkfa_film_record_year': 1960,
            'hkfa_source_page': 'https://www.filmarchive.gov.hk/en/web/hkfa/pe-event-2017-9-1-7.html',
            'saved_hkfa_record': 'docs/reference/external/qiushuang-zhai/hkfa-enchanting-shadow-source.json',
            'scope': 'The channel year is preserved verbatim, not adopted as verified release year.'}
    write_json(SUPPORT / (name + '-publisher.json'), metadata)
    trailers[name] = metadata

rights = json.load(open(NIGHT / 'celestial-company-source.json'))
copy_exact(NIGHT / 'celestial-company.html', SUPPORT / 'celestial-company.html', rights['sha256'])
write_json(SUPPORT / 'celestial-company-source.json', rights)
copy_exact(pathlib.Path('/tmp/garden_extract_selected_night_references.py'), SUPPORT / 'executed-frame-extractor.py')

reviews = {
    'daoxiang-cun': 'The frame shows a thatched rustic dwelling with exposed bundles along the eave, rough matte walls, narrow timber/bamboo poles and a simple rail. Cool blue-gray fog separates the dark foreground and warm brown timber/red costume. Night or dusk appearance is inferred from the dark, cool scene treatment; no source caption supplies its time of day. This fills the generic Shaw built-set/lighting slot, not Daoxiang identity, measured thatch thickness, roof dimensions or an amber-door practical. Use neutral rough walls and brown thatch against restrained cool background rather than copying a uniform green grade.',
    'aojing-guan': 'A wet night lane has pale plaster walls, octagonal openings, puddle highlights, dark foreground cart/timber silhouettes and small warm lights at the distant gate. Blue/cool wall light and warm practicals separate materials without lighting the entire foreground. Night appearance is a visual inference from the dark exterior and visible lamps. This supplies the generic night-set lighting slot only: it is a street, not Aojing or a water-level reflection hall, and proves no pond waterline, dry ledge, facade dimensions or one-window placement. The low-resolution frame cannot establish fine plaster texture.',
    'longcui-an': 'An upward view of a timber inn entrance shows a sign, exposed roof members, dark recesses and a bare branch against a mostly black background. Cool edges contrast with brown/gold timber and lettering. Night appearance is inferred visually, not a verified scene caption. It guides sparse branch silhouettes, timber separation and dark entrance framing. It is not the Longcui nunnery, its paired closed gates, its measured frontage or plum blossom material, and the low-resolution image cannot supply detailed joinery.',
    'qinfang-ting': 'A low-key terrace exterior has a warm round lamp at the left, cool blue light at the right, near-black sky and roof/figure silhouettes, and a broad central area that remains unlit. This fills the specified Shaw night-exterior lighting reference: limited cool wash, localized warm practical and dark space between. Night appearance is visually inferred. It does not identify Qinfang or show the four-exit Come Drink With Me bridge pavilion, and it provides no measured colors, light-linking configuration or lamp energy. Use the contrast pattern while reducing the green contribution as the user requested.',
    'ouxiang-xie': 'An open red-column pavilion has cream stone balustrades and a raised platform, a dark roof with gold beam details, a warm floor/column treatment and saturated blue foliage behind it. The table and open bays read against dark roof recesses. Night appearance is inferred from the dark exterior and cool/warm separation. This fills the generic night-set/built-structure lighting slot, not Ouxiang identity: water, support heights, exact dimensions, six seats and two lanterns are not established. Preserve warm wood, neutral stone and restrained blue background separation rather than reproducing the saturated source hue.',
    'daguan-lou': 'The court detail shows red posts, cream stone railing, a tiered gold ornament/table and localized warm candles against blue-lit foliage and dark structural recesses. The retained subtitle refers to midnight; the night treatment is also visible. It supplies a generic court night-set/material-separation reference, not Daguan identity, its full imperial facade, two-storey structure, roof geometry or surveyed proportions. The low-resolution source supports broad color and lighting hierarchy rather than fine painted-bracket or tile detail.',
    'tubi-tang': 'A tiered pagoda-like upright form is illuminated blue through a dark mesh of branches, with near-black surroundings and small warm/red detail. Night appearance is visually inferred. It demonstrates separating an elevated architectural silhouette from foreground foliage with a restricted cool wash while retaining darkness. This fills the generic Shaw night-set lighting slot, not Tubi identity, hill height, stair count, terrace dimensions or the required stone table. It is not a source model or a detailed construction photograph.',
    'ziling-zhou': 'A ruined brick opening and sparse table/bench dressing are framed by dark foliage; blue-lit leaves and masonry edges sit beside a warmer lit figure. Large black gaps keep the foreground sparse and layered. Night appearance is visually inferred from the dark exterior and directed cool/warm treatment. This guides generic night foliage and built-set composition, not Ziling identity, reed species, island geometry, waterline or footbridge construction. The separate close reed reference supplies botanical form; the saturated source blue is qualitative lighting guidance.'}

extraction = json.load(open(NIGHT / 'selected/extraction-report.json'))
assert len(extraction['frames']) == 8
assert len({x['frame_sha256'] for x in extraction['frames']}) == 8
archive_frames = []
for frame in extraction['frames']:
    site, slot, name = frame['site'], frame['slot'], frame['trailer']
    folder = ROOT / 'docs/reference/external' / site
    publisher = trailers[name]
    image_name = name + '-night-set.png'
    source = pathlib.Path(frame['path'])
    if site == 'daoxiang-cun':
        assert source.read_bytes() == (FIRST / 'daoxiang-night-exact.png').read_bytes()
    copy_exact(source, folder / image_name, frame['frame_sha256'])
    log = SUPPORT / (site + '-extraction.log')
    copy_exact(pathlib.Path(frame['log']), log, frame['log_sha256'])
    size = struct.unpack('>II', source.read_bytes()[16:24])
    archive_frame = dict(frame)
    archive_frame.update(saved_frame=str((folder / image_name).relative_to(ROOT)),
                         saved_log=str(log.relative_to(ROOT)),
                         saved_video=publisher['saved_video'],
                         dimensions=list(size), visually_reviewed_at='2026-10-08',
                         visual_review=reviews[site], accepted_reference_slot=slot)
    archive_frames.append(archive_frame)
    record = {
        'reference_slot': slot,
        'title': publisher['film'] + ' — night-set frame at ' + str(frame['actual_stream_pts_seconds']) + ' s in the published trailer',
        'photographer': 'Individual frame/still photographer uncredited; film produced by Shaw Brothers, trailer published by ' + publisher['channel'],
        'date': 'Trailer upload ' + publisher['upload_date'] + '; original capture date not supplied',
        'source_page': publisher['source_page'], 'original_source': publisher['source_page'],
        'publisher': publisher['channel'], 'publisher_channel': publisher['channel_url'],
        'license': 'Copyrighted Shaw Brothers film/trailer reference. Celestial library rights are documented; no open licence or redistribution permission is asserted.',
        'license_url': rights['url'],
        'local_file': image_name, 'sha256': frame['frame_sha256'], 'dimensions': list(size),
        'source_video': publisher['saved_video'], 'source_video_sha256': frame['source_video_sha256'],
        'actual_stream_pts': frame['actual_stream_pts'], 'actual_stream_pts_seconds': frame['actual_stream_pts_seconds'],
        'publisher_metadata': str((SUPPORT / (name + '-publisher.json')).relative_to(ROOT)),
        'extraction_log': str(log.relative_to(ROOT)), 'extraction_log_sha256': frame['log_sha256'],
        'changes': 'One frame decoded from the retained downloaded video stream to PNG with FFmpeg. No crop, resize or color grade was applied; publisher framing, bars and subtitles are retained. The PNG is a decoded video frame, not an original publisher JPEG.',
        'scope': 'Collected Shaw night-set lighting/built-set reference only; not a shipped game texture, measured model or named-site identification.',
        'visual_review': reviews[site], 'reviewed_at': '2026-10-08'}
    if name == 'enchanting-shadow': record['year_discrepancy'] = publisher['year_discrepancy']
    records = json.load(open(folder / 'sources.json'))
    assert all(x['reference_slot'] != slot for x in records)
    assert all(x['source_page'] != record['source_page'] for x in records)
    records.append(record)
    write_json(folder / 'sources.json', sorted(records, key=lambda x: x['reference_slot']))
    readme = folder / 'README.md'
    text = readme.read_text()
    replacements = {
        'One of three required references is collected: the named windowed facade.': 'Two of three required references are collected: the named windowed facade and a Shaw night-set lighting frame. The material close-view slot remains open.',
        'The Shaw Brothers night-set and distinguishing material close-view slots remain uncollected.': 'The distinguishing material close-view slot remains uncollected. The night-set frame is recorded below.',
        'Two of three required references are collected: site architecture and painted-wood details.': 'All three required references are collected: site architecture, painted-wood details and a Shaw night-set lighting frame.',
        'The Shaw Brothers night-set still remains uncollected.': 'The Shaw Brothers night-set frame is recorded below.',
        'Architecture and close material slots are collected; the sourced Shaw night-set still remains open.': 'Architecture, close material and sourced Shaw night-set slots are collected. Final scene art acceptance remains open.',
        'Architecture and close material slots are now collected; the sourced Shaw Brothers night-set slot remains open.': 'Architecture, close material and sourced Shaw night-set slots are collected. Final scene art acceptance remains open.',
        'Two of three required references are collected: the architecture and distinguishing foliage/material close views.': 'All three required references are collected: architecture, the foliage/material close view and a Shaw night-set lighting frame.',
        'The Shaw Brothers night-set slot remains uncollected.': 'The Shaw Brothers night-set frame is recorded below.',
        'One of the site’s three required references is collected.': 'Two of the site’s three required references are collected: the covered-bridge silhouette and Shaw night-exterior lighting. The specified Come Drink With Me bridge-pavilion frame remains open.',
        'The specified *Come Drink With Me* bridge-pavilion still and a suitable Shaw Brothers night-set lighting still remain uncollected.': 'The specified *Come Drink With Me* bridge-pavilion still remains uncollected. The night-set lighting frame is recorded below.',
        'Two of three required references are collected: hilltop architecture and a close foreground stone table surface.': 'All three required references are collected: hilltop architecture, a close foreground stone table surface and a Shaw night-set lighting frame.',
        'Two of three required references are collected: reed foliage and the identified modern entrance.': 'All three required references are collected: reed foliage, the identified modern entrance and a Shaw night-set lighting frame.'}
    for old, new in replacements.items(): text = text.replace(old, new)
    text += '\n## Collected night-set lighting reference — 2026-10-08\n\n'
    text += f'![{publisher["film"]} night-set reference]({image_name})\n\n'
    text += f'**{publisher["film"]}**, frame at {frame["actual_stream_pts_seconds"]} seconds in the [{publisher["channel"]} trailer]({publisher["source_page"]}), uploaded {publisher["upload_date"]}. '
    text += 'The individual frame photographer and capture date are not supplied. This is copyrighted reference material; no open licence is asserted. It is outside shipped game assets.\n\n'
    text += reviews[site] + '\n\n'
    text += f'Original downloaded stream and exact extraction provenance are retained in [the shared trailer archive](../supporting/shaw-trailers/README.md). The {size[0]} × {size[1]} decoded frame retains publisher framing, bars and subtitles, with no crop, resize or added color grade. SHA-256: `{frame["frame_sha256"]}`.\n'
    if name == 'enchanting-shadow': text += '\nThe trailer labels the film 1959; the saved Hong Kong Film Archive record gives 1960. The discrepancy is recorded without treating the channel year as verified.\n'
    readme.write_text(text)
    sheet = ROOT / 'docs/sites' / (site + '.md')
    text = sheet.read_text().replace('These are collection requirements, not claims that reference stills have been collected.',
        'Current saved references and any unfilled slots are recorded below and in the external reference README.')
    text += '\n## Collected Shaw night-set reference — 2026-10-08\n\n'
    text += f'Slot {slot} now has a directly reviewed frame from the published *{publisher["film"]}* trailer at {frame["actual_stream_pts_seconds"]} seconds. '
    text += reviews[site] + '\n\n'
    text += f'Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/{site}/README.md`. '
    missing = sorted({1, 2, 3} - {x['reference_slot'] for x in records})
    text += ('Remaining reference slots: ' + ', '.join(map(str, missing)) + '. ' if missing else 'All three reference slots are collected. ')
    text += 'This does not establish final scene art, lighting, performance or service acceptance.\n'
    sheet.write_text(text)

write_json(SUPPORT / 'selected-frame-provenance.json', {
    'status': 'eight_frames_directly_reviewed_and_saved',
    'scope': 'Reference selection/provenance only; no production scene/material changes or source-site identity claims.',
    'frames': archive_frames})

rejections = {
    'scope': 'Non-exhaustive trailer samples. Rejection means these reviewed images do not fill the specified slot, not that the film or trailer contains no suitable shot.',
    'items': [
        {'trailer': 'come-drink', 'sample': 'frame-002.png', 'source_page': trailers['come-drink']['source_page'],
         'reason': 'A daylight stone arch bridge beside an inn is visible; the specified four-exit bridge pavilion is not established. Qinfang slot 1 remains open.'},
        {'trailer': 'shaolin36', 'sample': 'frame-022.png', 'source_page': 'https://www.youtube.com/watch?v=9e4HDsEJfro',
         'reason': 'A training vat/figure crop does not establish the specified bare cell, single source and brighter doorway. Terminal slot 1 remains open.'},
        {'trailer': 'magic-blade', 'sample': 'frame-022.png', 'source_page': trailers['magic-blade']['source_page'],
         'reason': 'A fallen figure on tightly cropped stone ground does not establish a cave corridor. Rockery slot 2 remains open.'},
        {'trailer': 'enchanting-shadow', 'sample': 'frame-017.png', 'source_page': trailers['enchanting-shadow']['source_page'],
         'reason': 'A brush/paper/table view does not establish a night exterior or courtyard. Hengwu slot 1 remains open.'}]}
for item in rejections['items']:
    folder = FIRST if item['trailer'] in ('come-drink', 'shaolin36') else NIGHT
    source = folder / item['trailer'] / item['sample']
    destination = SUPPORT / ('rejected-' + item['trailer'] + '-' + item['sample'])
    item['saved_sample_sha256'] = copy_exact(source, destination)
    item['saved_sample'] = str(destination.relative_to(ROOT))
    trailer_report = json.load(open(folder / 'report.json'))
    source_item = next(x for x in trailer_report['items'] if x['name'] == item['trailer'])
    sampled = next(x for x in source_item['sample_frames'] if pathlib.Path(x['path']).name == item['sample'])
    assert sampled['sha256'] == item['saved_sample_sha256']
    item['sample_window_seconds'] = sampled['sample_window_seconds']
    item['source_video_sha256'] = source_item['sha256']
    item['timing_scope'] = 'Sampling window only, not exact PTS; exact decoded PTS is retained separately for accepted frames.'
write_json(SUPPORT / 'rejected-samples.json', rejections)

readme = '''# Shaw Brothers trailer lighting references

Eight distinct decoded frames fill eight generic night-set reference slots. Each frame was directly reviewed at its original decoded size. Three downloaded distributor video streams are retained byte for byte; exact commands, first selected stream PTS, extracted PNG hashes and FFmpeg logs are recorded in `selected-frame-provenance.json`. These references are outside the shipped Godot assets. No crop, resize or added color grade was applied to the saved frames; publisher framing, bars and subtitles remain.

The sources are [Arrow Video's Come Drink With Me trailer](https://www.youtube.com/watch?v=astCEpTZTiw), [Shaw Brothers Clips' Magic Blade trailer](https://www.youtube.com/watch?v=FU-5zusTJSY) and [Shaw Brothers Clips' Enchanting Shadow trailer](https://www.youtube.com/watch?v=oJ_Sy5j1XYU). Publisher metadata preserves titles, channels, upload dates and descriptions, together with the raw downloaded metadata hash. Temporary streaming URLs and format lists are omitted. The stream filenames are local archive names, not publisher titles.

[Celestial Pictures' company page](https://www.celestialpictures.com/company.php) describes its ownership of the Shaw film library. Its original HTML snapshot and hash are retained. Ownership/public trailer availability does not grant an open licence; no redistribution permission is asserted. Individual frame photographers and capture dates are uncredited. Reference collection does not authorize shipping these frames as textures or artwork.

The Enchanting Shadow trailer labels the film 1959. The [Hong Kong Film Archive record](https://www.filmarchive.gov.hk/en/web/hkfa/pe-event-2017-9-1-7.html), already saved in the Qiushuang reference folder, gives 1960 and Celestial copyright attribution. Both source statements are retained; the channel year is not treated as verified. The 600 × 480 Shaw trailer streams support broad layout/light/material contrast, not fine joinery or measured color values.

The selected frames distinguish warm wood and lamps, cream/gray stone or plaster, restricted blue foliage/background light and dark unlit areas. This is guidance for the user's less-green revision, not a copied grade, a measured light setup or final scene acceptance. The selected films do not identify any named garden site.

Rejected sample images and reasons are retained separately in `rejected-samples.json`. The sampled Come Drink With Me stone bridge does not establish the required bridge pavilion; a 36th Chamber training-vat crop does not establish a cell; Magic Blade stone ground does not establish a cave corridor; an Enchanting Shadow writing-table crop does not establish Hengwu night-exterior lighting. These slots remain open. The sample windows are approximate, while accepted-frame PTS values are exact decoder observations.
'''
readme += '\n| Site | Slot | Film | Trailer PTS (s) |\n| --- | --- | --- | --- |\n'
for x in archive_frames:
    readme += f'| [{x["site"]}](../../{x["site"]}/README.md) | {x["slot"]} | {trailers[x["trailer"]]["film"]} | {x["actual_stream_pts_seconds"]} |\n'
(SUPPORT / 'README.md').write_text(readme)
print('Saved eight distinct exact decoded frames and three unchanged source streams.')
