from PIL import Image
import os

input_folder = "/Users/mateobauvir/Desktop/UCL/Others_during_studies/Orchestra/2024-2025/Site-Orchestrakot-main/Site-Orchestrakot/images"
output_folder = "images/"

# Crée le dossier de sortie s’il n’existe pas
os.makedirs(output_folder, exist_ok=True)

for root, dirs, files in os.walk(input_folder):
    for filename in files:
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(root, filename)
            relative_path = os.path.relpath(root, input_folder)
            output_dir = os.path.join(output_folder, relative_path)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)

            try:
                img = Image.open(img_path)
                img.save(output_path, optimize=True, quality=50)
                print(f"Compressed: {output_path}")
            except Exception as e:
                print(f"Error compressing {img_path}: {e}")

print("compression terminée avec succès")
