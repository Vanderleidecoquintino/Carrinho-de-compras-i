import os, shutil, glob
from google.colab import files
from ultralytics import YOLO
import matplotlib.pyplot as plt

# 1. LIMPA TUDO
!rm -rf meu_dataset runs

# 2. RECRIA
!mkdir -p meu_dataset/images/train meu_dataset/images/val meu_dataset/labels/train meu_dataset/labels/val

# 3. PEGA SUAS FOTOS (as 5 que você subiu)
fotos = glob.glob("/content/*.jpg") + glob.glob("/content/*.jpeg") + glob.glob("/content/*.JPG")
if len(fotos) == 0:
    fotos = glob.glob("*.jpg") + glob.glob("*.jpeg")

print(f"Achei {len(fotos)} fotos")

# Se não achou, sobe de novo:
if len(fotos) == 0:
    print("Suba as 5 fotos agora!")
    uploaded = files.upload()
    fotos = list(uploaded.keys())

# 4. BOX CORRETO pra essa garrafa azul da sua foto
# Centro no meio, pega 50% da largura e 90% da altura
BOX = "0 0.50 0.52 0.48 0.90"

for i, f in enumerate(fotos[:5]):
    nome = f"img_{i}.jpg"
    label = f"img_{i}.txt"
    dest_img = "meu_dataset/images/train/" if i < 4 else "meu_dataset/images/val/"
    dest_lbl = "meu_dataset/labels/train/" if i < 4 else "meu_dataset/labels/val/"
    shutil.copy(f, dest_img + nome)
    with open(dest_lbl + label, "w") as out:
        out.write(BOX)

# 5. DATA.YAML com caminho ABSOLUTO
yaml = """
path: /content/meu_dataset
train: /content/meu_dataset/images/train
val: /content/meu_dataset/images/val
nc: 1
names: ['ketchup_quero']
"""
with open("/content/meu_dataset/data.yaml", "w") as out:
    out.write(yaml)

print("Dataset OK:")
!ls /content/meu_dataset/images/train && ls /content/meu_dataset/labels/train && cat /content/meu_dataset/data.yaml

# 6. TREINA FORÇADO
model = YOLO("yolo11n.pt")
model.train(data="/content/meu_dataset/data.yaml", epochs=200, imgsz=640, batch=2, patience=0, mosaic=0, hsv_h=0.0, hsv_s=0.0)

# 7. TESTA AUTOMATICO
best = "runs/detect/train/weights/best.pt"
model = YOLO(best)
results = model("/content/meu_dataset/images/train/", conf=0.10)

for r in results:
    plt.imshow(r.plot())
    plt.axis('off')
    plt.show()
    print(r.boxes)

files.download(best)
