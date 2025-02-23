from google.protobuf.descriptor_pb2 import FileDescriptorProto
import re

with open("v4-proto-py/v4_proto_amino/amino_pb2.py", "r") as f:
    content = f.read()

m = re.search(r"DESCRIPTOR = .*?AddSerializedFile\((b.*?)\)", content, re.DOTALL)
if m:
    desc_bytes = eval(m.group(1))
    print(f"Descriptor size: {len(desc_bytes)} bytes")
    print(f"First 50 bytes hex: {desc_bytes[:50].hex()}")
else:
    print("Could not find descriptor in file")
