import os

PNG_SIGNATURES = [(0x89, 0x50, 0x4E), (0x47, 0x49, 0x46), (0xFF, 0xD8, 0xFF)]


def get_xor_key(dat_file_path: str) -> int:
    """
    根据文件头信息获取异或密钥
    """
    with open(dat_file_path, "rb") as dat_file:
        header = dat_file.read(3)
        for signature in PNG_SIGNATURES:
            xor_key = bytes([a ^ b for a, b in zip(header, signature)])
            if xor_key.count(xor_key[0]) == len(xor_key):
                return xor_key[0]
    raise ValueError(f"无法从文件 {dat_file_path} 中获取有效的异或密钥")


def decode_image(dat_file_path: str, output_path: str) -> None:
    """
    将dat文件解码为jpg图像文件
    """
    xor_key = get_xor_key(dat_file_path)

    with open(dat_file_path, "rb") as dat_file, open(output_path, "wb") as jpg_file:
        dat_file.seek(0)  # 确保从文件头开始读取
        for chunk in iter(lambda: dat_file.read(1024), b""):
            decoded_chunk = bytes(byte ^ xor_key for byte in chunk)
            jpg_file.write(decoded_chunk)


def batch_decode_dat(dir_path: str) -> None:
    """
    对指定目录下的所有dat文件进行解码
    """
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            base_name, _ = os.path.splitext(file_name)
            decode_image(file_path, f"./jpgs/{base_name}.jpg")

