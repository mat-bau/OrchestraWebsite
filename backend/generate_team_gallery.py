import json
from pathlib import Path
from collections import defaultdict


def load_team_profiles():
    """Charge les profils des membres depuis team-profiles.json"""
    root_dir = Path(__file__).parent.parent.absolute()
    profiles_file = root_dir / 'team-profiles.json'
    
    with open(profiles_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_school_year(year):
    """Convertit une année en année scolaire (ex: 2024 -> 2024-2025)"""
    return f"{year}-{year + 1}"


def get_member_image_for_year(member, year):
    """Récupère l'image correspondant à une année spécifique"""
    if member['annee_debut'] > year or member['annee_fin'] < year:
        return None
    
    year_index = year - member['annee_debut']
    
    # Return the image at the index, or the last image if not enough images
    if year_index < len(member['images']):
        return member['images'][year_index]
    
    return member['images'][-1] if member['images'] else None


def is_member_in_year(member, year):
    """Vérifie si un membre était présent pendant une année scolaire donnée"""
    return member['annee_debut'] <= year < member['annee_fin']


def get_role_for_year(member, year):
    """Récupère le rôle d'un membre pour une année spécifique"""
    school_year = get_school_year(year)
    roles = member.get('roles', '')
    
    if isinstance(roles, dict):
        return roles.get(school_year, "")
    
    return roles if isinstance(roles, str) else ""


def get_etudes_for_year(member, year):
    """Récupère les études d'un membre pour une année spécifique"""
    school_year = get_school_year(year)
    etudes = member.get('etudes', '')
    
    if isinstance(etudes, dict):
        return etudes.get(school_year, "")
    
    return etudes if isinstance(etudes, str) else ""


def generate_par_annee_structure(profiles):
    """Génère la structure 'Par année' avec tri par rôle"""
    years = set()
    
    for member in profiles['members']:
        for year in range(member['annee_debut'], member['annee_fin']):
            years.add(year)
    
    ROLE_PRIORITY = {
        "président": 0,
        "vice-président": 1,
        "trésorier": 2,
        "trésorière": 2,
        "secrétaire": 3
    }
    
    folders = []
    for year in sorted(years, reverse=True):
        school_year = get_school_year(year)
        members_in_year = []
        
        for member in profiles['members']:
            if is_member_in_year(member, year):
                image_path = get_member_image_for_year(member, year)
                
                if image_path:
                    role = get_role_for_year(member, year)
                    etudes = get_etudes_for_year(member, year)
                    
                    description_parts = []
                    if role:
                        description_parts.append(role)
                    description_parts.append(' - '.join(member['instruments']))
                    if etudes:
                        description_parts.append(etudes)
                    
                    members_in_year.append({
                        "name": member['name'],
                        "path": image_path,
                        "description": ' - '.join(description_parts),
                        "role": role,  # Keep for HTML sorting
                        "role_priority": ROLE_PRIORITY.get(role.lower(), 999) if role else 999
                    })
        
        # Sort by role priority, then by name
        members_in_year.sort(key=lambda x: (x['role_priority'], x['name']))
        
        # Remove role_priority but KEEP role field for HTML
        for member in members_in_year:
            member.pop('role_priority', None)
        
        if members_in_year:
            folders.append({
                "name": school_year,
                "images": members_in_year
            })
    
    return folders


def generate_par_instrument_structure(profiles):
    """Génère la structure 'Par instrument'"""
    instruments_dict = {}
    
    for member in profiles['members']:
        for instrument in member['instruments']:
            if instrument not in instruments_dict:
                instruments_dict[instrument] = []
            
            # Use the most recent image
            image_path = member['images'][-1] if member['images'] else None
            
            if image_path:
                # Show year range
                description = f"{member['annee_debut']}-{member['annee_fin']}"
                
                instruments_dict[instrument].append({
                    "name": member['name'],
                    "path": image_path,
                    "description": description
                })
    
    folders = []
    for instrument in sorted(instruments_dict.keys()):
        folders.append({
            "name": instrument,
            "images": instruments_dict[instrument]
        })
    
    return folders


def generate_team_structure():
    """Génère la structure complète de l'équipe avec photos de groupe"""
    root_dir = Path(__file__).parent.parent.absolute()
    profiles_file = root_dir / 'team-profiles.json'
    
    if not profiles_file.exists():
        print(f"❌ Fichier {profiles_file} introuvable")
        return None
    
    with open(profiles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    members = data.get('members', [])
    team_photos = data.get('team_photos', {})
    
    # Define role priority for sorting
    ROLE_PRIORITY = {
        "président": 0,
        "vice-président": 1,
        "trésorier": 2,
        "trésorière": 2,
        "secrétaire": 3
    }
    
    # Organize members by year
    members_by_year = defaultdict(list)
    
    for member in members:
        start_year = member['annee_debut']
        end_year = member['annee_fin']
        
        for year in range(start_year, end_year):
            school_year = get_school_year(year)
            
            # Get image for this year
            image_path = get_member_image_for_year(member, year)
            
            # Get etudes and role for this year
            etudes = get_etudes_for_year(member, year)
            role = get_role_for_year(member, year)
            
            if image_path:
                members_by_year[school_year].append({
                    'name': member['name'],
                    'image': image_path,
                    'instruments': member['instruments'],
                    'etudes': etudes,
                    'role': role,
                    'role_priority': ROLE_PRIORITY.get(role.lower(), 999) if role else 999
                })
    
    # Build year folders structure
    years_folders = []
    for school_year in sorted(members_by_year.keys(), reverse=True):
        year_members = members_by_year[school_year]
        
        # Sort by role priority, then by name
        year_members.sort(key=lambda x: (x['role_priority'], x['name']))
        
        # Create member images
        member_images = []
        for member in year_members:
            # Build description (everything except name)
            description_parts = []
            if member['role']:
                description_parts.append(member['role'])
            if member['instruments']:
                description_parts.append(' - '.join(member['instruments']))
            if member['etudes']:
                description_parts.append(member['etudes'])
            
            member_images.append({
                "name": member['name'],  # For HTML display
                "path": member['image'],
                "description": ' - '.join(description_parts),  # For HTML hover
                "role": member['role']  # Keep for HTML sorting
            })
        
        years_folders.append({
            "name": school_year,
            "images": member_images,
            "folders": []
        })
    
    # Réutiliser la fonction generate_par_instrument_structure pour éviter la duplication
    instrument_folders_data = generate_par_instrument_structure(data)
    
    # Convertir au format attendu (ajouter folders: [])
    instrument_folders = []
    for folder in instrument_folders_data:
        instrument_folders.append({
            "name": folder["name"],
            "images": folder["images"],
            "folders": []
        })
    
    # Final structure
    team_structure = {
        "name": "Nos équipes",
        "folders": [
            {
                "name": "Par années",
                "folders": years_folders,
                "images": []
            },
            {
                "name": "Par instrument",
                "folders": instrument_folders,
                "images": []
            }
        ],
        "images": []
    }
    
    return team_structure


def merge_with_existing_gallery(team_structure):
    """Fusionne la structure de l'équipe avec la galerie existante"""
    root_dir = Path(__file__).parent.parent.absolute()
    gallery_file = root_dir / 'frontend' / 'gallery-structure.json'
    profiles_file = root_dir / 'team-profiles.json'
    
    with open(profiles_file, 'r', encoding='utf-8') as f:
        profiles_data = json.load(f)
    team_photos_dict = profiles_data.get('team_photos', {})
    
    existing_gallery = {"folders": [], "images": []}
    if gallery_file.exists():
        try:
            with open(gallery_file, 'r', encoding='utf-8') as f:
                existing_gallery = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing gallery: {e}")
    
    existing_folders = [f for f in existing_gallery.get('folders', []) 
                       if f.get('name') != 'Nos équipes']
    new_folders = [team_structure] + existing_folders
    
    return {
        "folders": new_folders,
        "images": existing_gallery.get('images', []),
        "team_photos": team_photos_dict
    }

if __name__ == '__main__':
    team_structure = generate_team_structure()
    
    if team_structure:
        final_gallery = merge_with_existing_gallery(team_structure)
        root_dir = Path(__file__).parent.parent.absolute()
        output_file = root_dir / 'frontend' / 'gallery-structure.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_gallery, f, indent=2, ensure_ascii=False)
        
        print(f"Gallery structure saved to {output_file}")