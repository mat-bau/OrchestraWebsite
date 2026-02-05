import os
import subprocess
import sys

# --- CONFIGURATION ---
MAX_SIZE_MB = 1.0  # Limite de taille par fichier pour le commit
IMAGE_DIR = "images/to_compress/compressed"
# ---------------------

def get_staged_files():
    """Récupère la liste des fichiers JPG ajoutés au staging git."""
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
    files = result.stdout.splitlines()
    return [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]

def check_file_sizes(files):
    """Vérifie si des fichiers dépassent la limite."""
    too_large = []
    for f in files:
        if os.path.exists(f):
            size_mb = os.path.getsize(f) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                too_large.append((f, size_mb))
    return too_large

def main():
    staged_images = get_staged_files()
    
    if not staged_images:
        print("❓ Aucun fichier image en staging. Faites d'abord 'git add'.")
        return

    large_files = check_file_sizes(staged_images)

    if large_files:
        print(f"⚠️  ATTENTION: Fichiers trop gros détectés:")
        for f, size in large_files:
            print(f"   📦 {f}: {size:.2f} Mo")
        
        print(f"\n💡 Utilisez 'python compress_images.py' pour réduire leur taille.")
        print(f"\n❌ COMMIT BLOQUÉ:")
        print(f"   Limite autorisée : {MAX_SIZE_MB} Mo par fichier.")
        sys.exit(1)

    # Si tout est OK, on tente le commit
    commit_msg = input("Entrez votre message de commit : ")
    subprocess.run(['git', 'commit', '-m', commit_msg])
    
    # Simulation du message de restant (optionnel)
    # Dans un vrai flux, on compterait les fichiers restants dans le dossier source
    print(f"\n✅ Commit réussi.")
    print(f"💡 N'oubliez pas de faire 'git push' pour envoyer sur GitHub.")

if __name__ == "__main__":
    main()