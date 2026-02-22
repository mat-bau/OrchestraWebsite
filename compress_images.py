import os
from PIL import Image

def compress_images(directory, quality=70):
    """
    Parcourt un dossier et compresse les images JPG/JPEG.
    :param directory: Chemin du dossier contenant les images
    :param quality: Qualité de sortie (1-95, 75 est un bon compromis)
    """
    # Formats acceptés
    extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    output_dir = os.path.join(directory, "compressed")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(directory):
        if filename.endswith(extensions):
            filepath = os.path.join(directory, filename)
            img = Image.open(filepath)
            output_path = os.path.join(output_dir, filename)
            img.save(output_path, "JPEG", optimize=True, quality=quality)
            
            print(f"Compressé : {filename} -> {output_dir}")

if __name__ == "__main__":
    # --- CONFIGURATION ---
    target_folder = "images/to_compress" 
    target_quality = 70# pourcentage de la qualité de base
    # ---------------------
    
    compress_images(target_folder, target_quality)