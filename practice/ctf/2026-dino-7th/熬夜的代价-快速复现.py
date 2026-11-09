"""本题复现：使用已验证密码，不修改输入 ZIP。依赖 Pillow、NumPy。"""
from pathlib import Path
from io import BytesIO
import sys,struct,zipfile,zlib
from PIL import Image
import numpy as np

src=Path(sys.argv[1])
out=Path(sys.argv[2] if len(sys.argv)>2 else '复现输出')
out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(src) as z:
    jpg=z.read('ccc.jpg')
start=jpg.index(b'PK\x03\x04')
eocd=jpg.index(b'PK\x05\x06',start)
comment=struct.unpack_from('<H',jpg,eocd+20)[0]
embedded=bytearray(jpg[start:eocd+22+comment])
pos=0
while True:
    pos=embedded.find(b'PK\x01\x02',pos)
    if pos<0:break
    local=struct.unpack_from('<I',embedded,pos+42)[0]
    localflags=struct.unpack_from('<H',embedded,local+6)[0]
    centralflags=struct.unpack_from('<H',embedded,pos+8)[0]
    if not(localflags&1) and (centralflags&1):
        struct.pack_into('<H',embedded,pos+8,centralflags&~1)
    pos+=46
(out/'embedded-fixed.zip').write_bytes(embedded)
with zipfile.ZipFile(BytesIO(embedded)) as z:
    hint=z.read('hint.txt')
    crc_zip=z.read('cccccrcc.zip',pwd=b'neworld')
    xor_zip=z.read('xxxxor.zip',pwd=b'neworld')
(out/'hint.txt').write_bytes(hint)
(out/'cccccrcc.zip').write_bytes(crc_zip)
(out/'xxxxor.zip').write_bytes(xor_zip)
lookup={zlib.crc32(bytes([i])):chr(i) for i in range(256)}
with zipfile.ZipFile(BytesIO(crc_zip)) as z:
    entries=sorted(z.infolist(),key=lambda i:int(i.filename.split('.')[0]))
    assert all(i.file_size==1 for i in entries)
    mask=''.join(lookup[i.CRC] for i in entries)
print('CRC 还原的密码格式：',mask)
assert mask=='D1no_????_2026'
with zipfile.ZipFile(BytesIO(xor_zip)) as z:
    final=z.read('final.png',pwd=b'D1no_newo_2026')
(out/'final.png').write_bytes(final)
signature=b'\x89PNG\r\n\x1a\n'
assert final.startswith(signature)
offset=8
while True:
    size=struct.unpack_from('>I',final,offset)[0]
    kind=final[offset+4:offset+8]
    offset+=12+size
    if kind==b'IEND':break
assert final[offset:offset+8]==signature
first,second=final[:offset],final[offset:]
(out/'first.png').write_bytes(first)
(out/'second.png').write_bytes(second)
a=np.array(Image.open(BytesIO(first)))
b=np.array(Image.open(BytesIO(second)))
assert a.shape==b.shape
Image.fromarray(np.bitwise_xor(a,b)).save(out/'最终结果.png')
print('已生成：',out/'最终结果.png')
