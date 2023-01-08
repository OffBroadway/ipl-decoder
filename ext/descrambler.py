import cslug

import sys
import os

import platform
import ctypes

script_template = """
#!/bin/sh
{0} cc $@
""".lstrip()

plat = platform.uname()
system = plat.system

class Descrambler():
    DECRYPT_START_OFFSET = 0x100
    CODE_START_OFFSET = 0x820

    def __init__(self) -> None:
        ext_path = os.path.abspath(__file__)
        ext_dir = os.path.dirname(ext_path)

        source = os.path.join(ext_dir, "descrambler.c")
        slug = cslug.CSlug(source)
        if not os.path.exists(slug.path):
            if system == "Windows":
                import io
                import zipfile
                import tempfile
                import urllib.request

                path = tempfile.TemporaryDirectory()
                url = "https://nongnu.askapache.com/tinycc/tcc-0.9.27-win64-bin.zip"
                r = urllib.request.Request(url)
                r.add_header("user-agent", "curl/7.86.0")

                with urllib.request.urlopen(r) as f:
                    zip_data = io.BytesIO(f.read())

                zip_ref = zipfile.ZipFile(zip_data)
                zip_ref.extractall(path.name)

                cc_path = os.path.join(path.name, "tcc", "tcc.exe")
            else:
                import ziglang
                zig_path = os.path.join(os.path.dirname(ziglang.__file__), "zig")

                cc_path = os.path.join(ext_dir, "zcc")
                if not os.path.exists(cc_path):
                    script = script_template.format(zig_path)
                    with open(cc_path, 'w') as f:
                        f.write(script)
                    mode = os.stat(cc_path).st_mode
                    mode |= 0o111
                    os.chmod(cc_path, mode)

            os.environ['CC'] = cc_path

        dll = slug.dll
        if system == "Windows":
            args = dll.Descrambler.argtypes
            dll = ctypes.WinDLL(str(slug.path))
            dll.argtypes = args

        self.descrambler = slug.dll.Descrambler

    def _get_code_end(self, data) -> int:
        stride_size = 0x20
        zero_stride = bytes([0x00] * stride_size)

        start = self.DECRYPT_START_OFFSET
        index = 0
        while index < len(data) - stride_size:
            index = data.index(zero_stride, start)
            if index % stride_size == 0:
                break

            start = index + (index % stride_size)
        return index

    def get_code(self, data) -> bytes:
        start = self.CODE_START_OFFSET - self.DECRYPT_START_OFFSET
        end = self._get_code_end(data)

        data = data[:end][self.DECRYPT_START_OFFSET:]
        ptr = ctypes.c_char_p(data)
        size = len(data)
        self.descrambler(ptr, size)

        return data[start:]

if __name__ == "__main__":
    filename = "ipl.bin"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    f = open(filename, 'rb')
    data = f.read()

    print(hex(len(data)))

    descrambler = Descrambler()
    ipl = descrambler.get_code(data)

    print(len(ipl), repr(ipl[:4]))
    with open('dec-ipl.bin', 'wb') as f:
        f.write(ipl)
