"""Recognize Git LFS pointer headers without changing stored asset bytes.

Matches Git LFS 3.8 v1Aliases and DecodeFrom's bytes.TrimSpace framing:
https://github.com/git-lfs/git-lfs/blob/v3.8.0/lfs/pointer.go
"""
_HEADERS = {
    b'version http://git-media.io/v/2',
    b'version https://hawser.github.com/spec/v1',
    b'version https://git-lfs.github.com/spec/v1',
}
# Unicode White_Space used by Go, including the Latin-1 space characters.
_SPACE = (' \t\n\r\v\f\u0085\u00a0\u1680'
          + ''.join(chr(value) for value in range(0x2000, 0x200b))
          + '\u2028\u2029\u202f\u205f\u3000')


def normalize_pointer(data):
    try:
        normalized = data.decode('utf-8').strip(_SPACE).replace('\r\n', '\n').encode('utf-8')
    except UnicodeDecodeError:
        return None
    return normalized if normalized.partition(b'\n')[0] in _HEADERS else None
