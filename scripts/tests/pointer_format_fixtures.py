"""Literal pointer encodings accepted by Git LFS 3.8; no production parser calls."""
def pointer_cases(oid, size):
    canonical = f'version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize {size}\n'.encode()
    hawser = canonical.replace(b'https://git-lfs.github.com/spec/v1', b'https://hawser.github.com/spec/v1')
    alpha = canonical.replace(b'https://git-lfs.github.com/spec/v1', b'http://git-media.io/v/2')
    return [
        ('canonical', canonical),
        ('leading_blanks', b'\n\n' + canonical),
        ('leading_ascii_space', b' \t' + canonical),
        ('leading_nbsp', '\u00a0'.encode() + canonical),
        ('leading_ideographic_space', '\u3000'.encode() + canonical),
        ('hawser', hawser),
        ('alpha', alpha),
        ('hawser_crlf_surrounded', b'\t\r\n' + hawser.replace(b'\n', b'\r\n') + '\u2000'.encode()),
        ('blank_lines_between_fields', canonical.replace(b'\n', b'\n\n')),
    ]
