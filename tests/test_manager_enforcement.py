import pytest
import os
import ast
from django.conf import settings

def test_no_raw_objects_all_in_views():
    # Scan all views.py to ensure models with managers don't use raw objects bypasses
    # We want to ensure .all_objects or .objects is used properly and there are no direct bypasses.
    # The actual enforcement was done by renaming managers, but let's statically check for
    # common mistakes like Warehouse._base_manager.all()
    project_root = settings.BASE_DIR
    views_dir = os.path.join(project_root, 'inventory', 'views')
    
    violations = []
    
    for root, _, files in os.walk(views_dir):
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Very simple check: does not contain _base_manager
                    if '_base_manager' in content or '_default_manager' in content:
                        violations.append(f"{f} uses internal manager bypass")
                        
    assert not violations, f"Manager enforcement violations found: {violations}"
