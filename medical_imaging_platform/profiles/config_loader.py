"""
config_loader.py
----------------
Load and validate organ profile YAML configurations
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

PROFILES_DIR = Path(__file__).parent


class OrgalProfileLoader:
    """Load and validate organ segmentation profiles"""
    
    REQUIRED_FIELDS = {
        'organ', 'description', 'category', 'modality',
        'tissues', 'preprocessing', 'morphology', 'mesh', 'export'
    }
    
    @staticmethod
    def load(organ_name: str) -> Dict[str, Any]:
        """Load organ profile YAML by name"""
        profile_path = PROFILES_DIR / f"{organ_name}.yaml"
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")
        
        with open(profile_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate
        OrgalProfileLoader._validate(config, organ_name)
        return config
    
    @staticmethod
    def _validate(config: Dict, organ_name: str) -> None:
        """Validate config has all required fields"""
        missing = OrgalProfileLoader.REQUIRED_FIELDS - set(config.keys())
        if missing:
            raise ValueError(f"Config '{organ_name}' missing fields: {missing}")
        
        # Validate tissues
        tissues = config.get('tissues', {})
        if not tissues:
            raise ValueError("At least one tissue must be defined")
        
        for tissue_name, tissue_config in tissues.items():
            required_tissue = {'name', 'hu_min', 'hu_max', 'color', 'description'}
            missing_tissue = required_tissue - set(tissue_config.keys())
            if missing_tissue:
                raise ValueError(
                    f"Tissue '{tissue_name}' missing fields: {missing_tissue}"
                )
    
    @staticmethod
    def list_available() -> list:
        """List all available organ profiles"""
        profiles = []
        for yaml_file in PROFILES_DIR.glob("*.yaml"):
            if yaml_file.name != '__init__.py':
                profiles.append(yaml_file.stem)
        return sorted(profiles)
    
    @staticmethod
    def get_tissue_by_name(config: Dict, tissue_name: str) -> Dict:
        """Get specific tissue config from organ profile"""
        tissues = config.get('tissues', {})
        if tissue_name not in tissues:
            raise KeyError(f"Tissue '{tissue_name}' not found in profile")
        return tissues[tissue_name]


if __name__ == "__main__":
    # Test
    print("Available profiles:")
    for profile in OrgalProfileLoader.list_available():
        print(f"  - {profile}")
    
    # Load brain profile
    print("\nLoading brain profile...")
    brain_config = OrgalProfileLoader.load('brain')
    print(f"✓ Loaded: {brain_config['organ']}")
    print(f"  Description: {brain_config['description']}")
    print(f"  Tissues: {list(brain_config['tissues'].keys())}")
