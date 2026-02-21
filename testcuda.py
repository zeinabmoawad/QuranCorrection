# import torch
# print(f"GPU: {torch.cuda.get_device_name(0)}")
# print(f"CUDA Version: {torch.version.cuda}")
# print(f"PyTorch Version: {torch.__version__}")
import torch
print(torch.__version__)
print(torch.cuda.is_available())