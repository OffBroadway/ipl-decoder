import pexpect
import ziglang
import os

# import distutils
import platform
import ctypes

systems_extensions = {
    "Windows": ".dll",
    "Darwin": ".dylib",
    "Linux": ".so",
}

plat = platform.uname()
system = plat.system

system_extension = systems_extensions[system]

class Descrambler():
    DECRYPT_START_OFFSET = 0x100
    CODE_START_OFFSET = 0x820

    def __init__(self) -> None:
        zig = os.path.join(os.path.dirname(ziglang.__file__), "zig")

        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)

        # compiler = distutils.ccompiler.new_compiler()
        # output = "libdescrambler" + compiler.shared_lib_extension
        output = "libdescrambler" + system_extension

        lib_path = os.path.join(script_dir, output)

        if not os.path.exists(lib_path):
            pexpect.run(f'{zig} cc -shared -o {output} descrambler.c', cwd=script_dir, withexitstatus=True)

        descrambler_lib = ctypes.CDLL(lib_path)

        descrambler = descrambler_lib.Descrambler 
        descrambler.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
        descrambler.restype = ctypes.c_uint32

        self.descrambler = descrambler

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
    import sys

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
