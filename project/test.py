# from cryptography.hazmat.primitives.asymmetric import ec
# from cryptography.hazmat.primitives import hashes

# def sign_data_with_ecc(data: str) -> str:
#     """
#     Ký dữ liệu bằng ECC và trả về chữ ký ở dạng hex.
    
#     :param data: Dữ liệu cần ký (dạng chuỗi)
#     :return: Chữ ký đã mã hóa ở dạng hex
#     """
#     # Tạo khóa ECC
#     private_key = ec.generate_private_key(ec.SECP256R1())  # SECP256R1 là elliptic curve thường dùng
    
#     # Chuyển dữ liệu thành bytes
#     data_bytes = data.encode()
    
#     # Ký dữ liệu
#     signature = private_key.sign(
#         data_bytes,
#         ec.ECDSA(hashes.SHA256())
#     )
    
#     # Chuyển chữ ký thành dạng hex và trả về
#     return signature.hex()

# # Ví dụ sử dụng hàm
# data = "Hello, ECC!"
# signature_hex = sign_data_with_ecc(data)
# print("Chữ ký đã mã hóa (dạng hex):", signature_hex)

# Sử dụng thư viện cryptography

from cryptography.hazmat.primitives.asymmetric import ec
from base64 import b64encode
from cryptography.hazmat.primitives import serialization
# Tạo khóa
private_key = ec.generate_private_key(ec.SECP256K1())
public_key = private_key.public_key()

# Dạng bytes
key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
# Chuyển sang Base64
key_b64 = b64encode(key_bytes).decode('utf-8')
print("Dạng Base64:", key_b64)