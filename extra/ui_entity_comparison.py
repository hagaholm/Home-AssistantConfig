#!/usr/bin/env python3
"""
UI Entity Comparison Script
Compares entities in UI files vs source configuration files
"""
import re
import yaml
from pathlib import Path
from collections import defaultdict

# Configuration
WORKSPACE = Path(r"c:\Users\micke\Documents\GitHub\Home-AssistantConfig")
UI_FILES = ["ui-automation.yaml", "ui-camera.yaml", "ui-climate.yaml", 
            "ui-lights.yaml", "ui-lovelace.yaml", "ui-ventilation.yaml"]

def extract_entities_from_text(content):
    """Extract all entity references from YAML content"""
    entities = set()
    
    # Pattern 1: entity: automation.name
    pattern1 = re.compile(r'entity:\s*([a-z_]+\.[a-z0-9_]+)', re.IGNORECASE)
    entities.update(pattern1.findall(content))
    
    # Pattern 2: - automation.name (in lists)
    pattern2 = re.compile(r'^\s*-\s+([a-z_]+\.[a-z0-9_]+)', re.MULTILINE)
    entities.update(pattern2.findall(content))
    
    # Pattern 3: entity_id: automation.name
    pattern3 = re.compile(r'entity_id:\s*([a-z_]+\.[a-z0-9_]+)', re.IGNORECASE)
    entities.update(pattern3.findall(content))
    
    # Pattern 4: target: entity_id:
    pattern4 = re.compile(r'entity_id:\s*([a-z_]+\.[a-z0-9_]+)', re.IGNORECASE)
    entities.update(pattern4.findall(content))
    
    return entities

def extract_defined_entities(content, filename):
    """Extract entity definitions from source files"""
    entities = set()
    
    # Look for entity definitions (e.g., automation:, input_boolean:, etc.)
    # Pattern: two spaces, entity name with underscores, colon
    pattern = re.compile(r'^\s{2}([a-z][a-z0-9_]+):\s*$', re.MULTILINE)
    matches = pattern.findall(content)
    
    # Try to infer domain from context or filename
    domain = None
    if 'automation:' in content:
        domain = 'automation'
    elif 'input_boolean:' in content:
        domain = 'input_boolean'
    elif 'input_select:' in content:
        domain = 'input_select'
    elif 'input_number:' in content:
        domain = 'input_number'
    elif 'script:' in content:
        domain = 'script'
    elif 'timer:' in content:
        domain = 'timer'
    elif 'counter:' in content:
        domain = 'counter'
    elif 'sensor:' in content:
        domain = 'sensor'
    elif 'binary_sensor:' in content:
        domain = 'binary_sensor'
    
    if domain:
        for match in matches:
            entities.add(f"{domain}.{match}")
    
    return entities

def main():
    print("=" * 80)
    print("HOME ASSISTANT UI ENTITY COMPARISON REPORT")
    print("=" * 80)
    print()
    
    # Step 1: Extract all entities from UI files
    print("📊 EXTRACTING ENTITIES FROM UI FILES...")
    print("-" * 80)
    
    ui_entities = set()
    ui_by_file = defaultdict(set)
    
    for ui_file in UI_FILES:
        filepath = WORKSPACE / ui_file
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            entities = extract_entities_from_text(content)
            ui_entities.update(entities)
            ui_by_file[ui_file] = entities
            print(f"  {ui_file:30s} {len(entities):4d} entities")
    
    print(f"\n  TOTAL UI ENTITIES: {len(ui_entities)}")
    print()
    
    # Step 2: Extract all entities from source files
    print("📊 EXTRACTING ENTITIES FROM SOURCE FILES...")
    print("-" * 80)
    
    source_entities = set()
    source_references = set()
    
    for yamlfile in WORKSPACE.rglob("*.yaml"):
        # Skip UI files and some system files
        if yamlfile.name in UI_FILES or yamlfile.name in ['customize.yaml', 'secrets.yaml']:
            continue
        if 'ui-' in yamlfile.name:
            continue
        
        try:
            content = yamlfile.read_text(encoding='utf-8')
            
            # Extract definitions
            defined = extract_defined_entities(content, yamlfile.name)
            source_entities.update(defined)
            
            # Extract references
            referenced = extract_entities_from_text(content)
            source_references.update(referenced)
            
        except Exception as e:
            pass  # Skip files with errors
    
    print(f"  Defined entities in source: {len(source_entities)}")
    print(f"  Referenced entities in source: {len(source_references)}")
    all_source = source_entities | source_references
    print(f"  TOTAL SOURCE ENTITIES: {len(all_source)}")
    print()
    
    # Step 3: Compare and categorize
    print("=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    print()
    
    # Entities in UI but NOT in source (might be obsolete)
    obsolete_in_ui = ui_entities - all_source
    
    # Entities in source but NOT in UI (might be missing from UI)
    missing_from_ui = all_source - ui_entities
    
    # Organize by type
    def organize_by_type(entity_set):
        by_type = defaultdict(list)
        for entity in sorted(entity_set):
            if '.' in entity:
                domain = entity.split('.')[0]
                by_type[domain].append(entity)
        return dict(sorted(by_type.items()))
    
    obsolete_by_type = organize_by_type(obsolete_in_ui)
    missing_by_type = organize_by_type(missing_from_ui)
    
    # Print results
    print("🔴 CAN BE REMOVED FROM UI (Not defined or used in source)")
    print("=" * 80)
    print(f"Total: {len(obsolete_in_ui)} entities\n")
    
    for entity_type, entities in obsolete_by_type.items():
        print(f"\n{entity_type.upper()} ({len(entities)}):")
        print("-" * 80)
        for entity in entities:
            print(f"  - {entity}")
    
    print("\n" + "=" * 80)
    print("🟢 MISSING IN UI (Defined/used in source but not in UI)")
    print("=" * 80)
    print(f"Total: {len(missing_from_ui)} entities\n")
    
    for entity_type, entities in missing_by_type.items():
        print(f"\n{entity_type.upper()} ({len(entities)}):")
        print("-" * 80)
        count = 0
        for entity in entities:
            print(f"  - {entity}")
            count += 1
            # Limit output for very large lists
            if count > 100:
                print(f"  ... and {len(entities) - count} more")
                break
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Entities in UI:                 {len(ui_entities)}")
    print(f"Entities in source:             {len(all_source)}")
    print(f"CAN BE REMOVED FROM UI:         {len(obsolete_in_ui)}")
    print(f"MISSING IN UI:                  {len(missing_from_ui)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
