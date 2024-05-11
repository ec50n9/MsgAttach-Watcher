import os

into_path = r"D:\Applications\WeChat\Files\WeChat Files\wxid_a4wk56tl3y7b22\FileStorage\MsgAttach\4e57d4ac0a4bd64c6f052e7e755bc2e9\Image\2024-05"  # 请将想导入的dat文件的路径复制到引号里面，修改此处代码
out_path = r"./jpgs/"  # 运行代码前记得修改导出路径，此处是导出到E盘的jpgs空文件夹下


def imageDecode(f, fn):
    dat_read = open(f, "rb")
    xo = Format(f)
    out = out_path + fn + ".jpg"
    print("导出文件的路径{}".format(out), end="\n\n")
    png_write = open(out, "wb")
    dat_read.seek(0)

    for now in dat_read:
        for nowByte in now:
            newByte = nowByte ^ xo
            png_write.write(bytes([newByte]))

    dat_read.close()
    png_write.close()


def findFile(f):
    fsinfo = os.listdir(f)
    print(fsinfo)
    for fn in fsinfo:
        temp_path = os.path.join(f, fn)
        if os.path.isfile(temp_path):
            print("导入的文件路径是{}".format(temp_path))
            fn = fn[:-4]
            imageDecode(temp_path, fn)
        else:
            pass


def Format(f):
    dat_r = open(f, "rb")
    try:
        a = [(0x89, 0x50, 0x4E), (0x47, 0x49, 0x46), (0xFF, 0xD8, 0xFF)]
        for now in dat_r:
            for xor in a:
                i = 0
                res = []
                nowg = now[:3]
                for nowByte in nowg:
                    res.append(nowByte ^ xor[i])
                    i += 1
                if res[0] == res[1] == res[2]:
                    return res[0]
    except:
        pass
    finally:
        dat_r.close()


if __name__ == "__main__":
    findFile(into_path)
