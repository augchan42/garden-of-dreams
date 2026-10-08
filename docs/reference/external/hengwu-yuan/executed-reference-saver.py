import hashlib,json,pathlib,shutil,urllib.parse
R=pathlib.Path('/Users/auchan/projects/garden-of-dreams')
C=pathlib.Path(json.load(open('/tmp/garden-aojing-material-candidates.json'))['folder'])
N=pathlib.Path(json.load(open('/tmp/garden-official-night-trailer-reference.json'))['folder'])
SUP=R/'docs/reference/external/supporting/shaw-trailers'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def copy(source,path,expected):
 assert sha(source)==expected and not path.exists()
 shutil.copyfile(source,path);assert sha(path)==expected

candidate=json.load(open(C/'results.json'))[0]
A=R/'docs/reference/external/aojing-guan'
copy(pathlib.Path(candidate['file']),A/'weathered-timber-glazing-close.jpg',candidate['sha256'])
assert hashlib.sha1((A/'weathered-timber-glazing-close.jpg').read_bytes()).hexdigest()==candidate['commons_sha1']
copy(pathlib.Path(candidate['metadata']),A/'timber-glazing-commons-source.json',candidate['metadata_sha256'])
ao_review='The close photograph shows dull weathered timber grain, chipped pale paint along the jambs and glazing bars, recessed clear panes, dark reflected foliage and thin surface dirt/webs. It supplies a timber-and-glazing surface reference for Aojing\'s shutter/window dressing. This is not verified Chinese or Aojing architecture, a survey, night lighting or a prescription to copy the shingle facade, pediment, grid proportions or extreme paint decay. Use grain/roughness and glass contrast only; retain the game\'s authored dark shutters, single amber window and stage-set treatment.'
record={'reference_slot':3,'title':candidate['title'],'photographer':'Fruehlingswiese','date':'2018-10-25 (source metadata)',
 'source_page':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(candidate['title'].replace(' ','_')),
 'original_source':candidate['source_url'],'photographer_source':'https://pixabay.com/photos/wooden-windows-lattice-windows-3768742/',
 'license':'CC0 1.0 (the saved Commons file record states an explicit author release for this image)',
 'license_url':'https://creativecommons.org/publicdomain/zero/1.0/deed.en',
 'local_file':'weathered-timber-glazing-close.jpg','sha256':candidate['sha256'],'commons_sha1':candidate['commons_sha1'],
 'source_metadata_file':'timber-glazing-commons-source.json','source_metadata_sha256':candidate['metadata_sha256'],
 'changes':'None; original downloaded JPEG bytes verified against the Commons imageinfo SHA-1. No crop, resize or color grade applied.',
 'scope':'Collected close timber/glazing material reference only; not a shipped texture, source model, named-site identification or night-set reference.',
 'visual_review':ao_review,'reviewed_at':'2026-10-08'}
records=json.load(open(A/'sources.json'));assert all(x['reference_slot']!=3 for x in records)
records.append(record);write(A/'sources.json',sorted(records,key=lambda x:x['reference_slot']))
t=(A/'README.md').read_text().replace('Two of three required references are collected: the named windowed facade and a Shaw night-set lighting frame. The material close-view slot remains open.', 'All three required references are collected: the named windowed facade, Shaw night-set lighting and a close timber/glazing surface photograph.').replace('The distinguishing material close-view slot remains uncollected. The night-set frame is recorded below.', 'The material close-view and night-set frames are recorded below.')
t+='\n## Collected close timber/glazing reference — 2026-10-08\n\n![Weathered timber and clear glazing](weathered-timber-glazing-close.jpg)\n\n**Wooden lattice window.jpg**, Fruehlingswiese, 25 October 2018 according to source metadata. [Commons source and author release]('+record['source_page']+'), [photographer source]('+record['photographer_source']+'), [CC0 1.0]('+record['license_url']+'). The saved Commons record states the image\'s explicit CC0 release; no blanket statement about current Pixabay licensing is made. Original JPEG bytes and raw imageinfo metadata are retained. SHA-256: `'+candidate['sha256']+'`; Commons SHA-1: `'+candidate['commons_sha1']+'`.\n\n'+ao_review+'\n'
(A/'README.md').write_text(t)

frame=json.load(open(N/'hengwu-frame-command.json'));H=R/'docs/reference/external/hengwu-yuan'
copy(pathlib.Path(frame['path']),H/'enchanting-shadow-night-wall.png',frame['frame_sha256'])
copy(pathlib.Path(frame['log']),H/'enchanting-shadow-night-extraction.log',frame['log_sha256'])
write(H/'enchanting-shadow-frame-provenance.json',frame)
publisher=json.load(open(SUP/'enchanting-shadow-publisher.json'))
assert sha(R/publisher['saved_video'])==frame['source_video_sha256']
heng_review='The frame shows a figure beside broken brick/plaster masonry and a dark geometric lattice opening. Restricted blue light picks out the window and rough masonry edges; warmer brown/amber accents distinguish the near wall and costume while branches and deep openings stay near black. Night appearance is inferred visually from the directed blue light and dark setting; no shot caption supplies the time of day. It fills the generic Shaw night-set lighting/built-set slot, not Hengwu identity, its complete courtyard, herb species, perforated rocks or dimensions. No amber room lamp is visible, and the reference branches do not authorize adding trees to Hengwu\'s required clear skyline. Use neutral stone/plaster against limited cool fill and warm accents without copying the saturated blue source grade.'
record={'reference_slot':1,'title':'The Enchanting Shadow — night wall/window frame at 53.0 s in the published trailer',
 'photographer':'Individual frame/still photographer uncredited; film produced by Shaw Brothers, trailer published by Shaw Brothers Clips',
 'date':'Trailer upload 2012-10-18; original capture date not supplied','source_page':publisher['source_page'],'original_source':publisher['source_page'],
 'publisher':publisher['channel'],'publisher_channel':publisher['channel_url'],
 'license':'Copyrighted Shaw Brothers film/trailer reference; no open licence or redistribution permission is asserted.',
 'license_url':'https://www.celestialpictures.com/company.php','local_file':'enchanting-shadow-night-wall.png','sha256':frame['frame_sha256'],
 'dimensions':[600,480],'source_video':publisher['saved_video'],'source_video_sha256':frame['source_video_sha256'],
 'actual_stream_pts':frame['actual_stream_pts'],'actual_stream_pts_seconds':frame['actual_stream_pts_seconds'],
 'publisher_metadata':'docs/reference/external/supporting/shaw-trailers/enchanting-shadow-publisher.json',
 'extraction_log':'enchanting-shadow-night-extraction.log','extraction_log_sha256':frame['log_sha256'],
 'changes':'One entire frame decoded from the retained downloaded stream to PNG. No crop, resize or color grade added; publisher bars/framing/subtitles retained. This is a decoded video frame, not an original publisher JPEG.',
 'scope':'Collected night-set lighting/built-set reference only; not a shipped texture, source model or Hengwu identification.',
 'visual_review':heng_review,'reviewed_at':'2026-10-08','year_discrepancy':publisher['year_discrepancy']}
records=json.load(open(H/'sources.json'));assert all(x['reference_slot']!=1 for x in records)
records.append(record);write(H/'sources.json',sorted(records,key=lambda x:x['reference_slot']))
t=(H/'README.md').read_text().replace('Two of three required references are collected:', 'All three required references are collected:')
t+='\n## Collected night-set reference — 2026-10-08\n\n![Night wall and lattice opening](enchanting-shadow-night-wall.png)\n\n**The Enchanting Shadow**, exact stream PTS 53.0 seconds in the [Shaw Brothers Clips trailer]('+publisher['source_page']+'), uploaded 18 October 2012. The source stream is already retained in the shared trailer archive. The decoded 600 × 480 frame, decoder log and exact command/PTS are retained here. The individual frame photographer and capture date are uncredited. Copyrighted reference material; no open licence is asserted. The trailer labels the film 1959; the saved Hong Kong Film Archive record gives 1960. Both source statements remain recorded. Frame SHA-256: `'+frame['frame_sha256']+'`.\n\n'+heng_review+'\n\nAll three reference slots are now collected. Final scene art, lighting and service acceptance remain open.\n'
(H/'README.md').write_text(t)
for site,slot,review in [('aojing-guan',3,ao_review),('hengwu-yuan',1,heng_review)]:
 p=R/'docs/sites'/(site+'.md');t=p.read_text().replace('These are collection requirements, not claims that reference stills have been collected.','Current saved references and any unfilled slots are recorded below and in the external reference README.')
 t+='\n## Completed reference collection — 2026-10-08\n\nSlot '+str(slot)+' now has a directly reviewed sourced reference. '+review+'\n\nAll three slots are collected; attribution, rights, originals and hashes are recorded in `../reference/external/'+site+'/README.md`. This does not establish final scene art or rendering/device/service acceptance.\n';p.write_text(t)
print('AOJING_SLOT3_HENGWU_SLOT1_SAVED')
