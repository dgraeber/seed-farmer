#!/usr/bin/env python3
"""
IDF Modules Documentation Generator for MkDocs

This script clones the AWS IDF modules repository and generates
structured MkDocs documentation from the README files.
"""

import os
import re
import git
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import shutil

class IDFDocsGenerator:
    def __init__(self, repo_url: str = "https://github.com/awslabs/idf-modules.git", 
                 output_dir: str = "docs/modules"):
        self.repo_url = repo_url
        self.output_dir = Path(output_dir)
        self.temp_dir = None
        
    def clone_repository(self) -> Path:
        """Clone the IDF modules repository to a temporary directory."""
        self.temp_dir = Path(tempfile.mkdtemp())
        print(f"Cloning repository to {self.temp_dir}")
        git.Repo.clone_from(self.repo_url, self.temp_dir, depth=1)
        return self.temp_dir / "modules"
    
    def discover_modules(self, modules_path: Path) -> Dict[str, List[str]]:
        """Discover all modules organized by category."""
        modules = {}
        
        for category_dir in modules_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                category = category_dir.name
                modules[category] = []
                
                for module_dir in category_dir.iterdir():
                    if module_dir.is_dir() and (module_dir / "README.md").exists():
                        modules[category].append(module_dir.name)
        
        return modules
    
    def parse_readme(self, readme_path: Path) -> Dict[str, str]:
        """Parse README.md and extract key sections."""
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = {}
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        sections['title'] = title_match.group(1) if title_match else "Untitled Module"
        
        # Extract description section
        desc_match = re.search(r'## Description\s*\n(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL)
        sections['description'] = desc_match.group(1).strip() if desc_match else ""
        
        # Extract inputs section
        inputs_match = re.search(r'### Input Parameters\s*\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        sections['inputs'] = inputs_match.group(1).strip() if inputs_match else ""
        
        # Extract outputs section  
        outputs_match = re.search(r'### Module Metadata Outputs\s*\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        sections['outputs'] = outputs_match.group(1).strip() if outputs_match else ""
        
        # Extract input example if available
        example_match = re.search(r'### Input Example\s*\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        sections['example'] = example_match.group(1).strip() if example_match else ""
        
        return sections
    
    def generate_module_page(self, category: str, module: str, sections: Dict[str, str]) -> str:
        """Generate MkDocs markdown for a single module."""
        markdown = f"""# {sections['title']}

**Category:** {category.title()}  
**Module:** `{category}/{module}`

## Description

{sections['description']}

"""
        
        if sections['inputs']:
            markdown += f"""## Input Parameters

{sections['inputs']}

"""
        
        if sections['outputs']:
            markdown += f"""## Outputs

{sections['outputs']}

"""
            
        if sections['example']:
            markdown += f"""## Example Usage

{sections['example']}

"""
        
        # Add link to source
        markdown += f"""## Source

[View on GitHub](https://github.com/awslabs/idf-modules/tree/main/modules/{category}/{module})
"""
        
        return markdown
    
    def generate_category_index(self, category: str, modules: List[str], 
                              all_sections: Dict[str, Dict[str, str]]) -> str:
        """Generate an index page for a category with expandable modules."""
        markdown = f"""# {category.title()} Modules

This section contains all {category} modules available in the IDF framework.

"""
        
        for module in sorted(modules):
            module_key = f"{category}/{module}"
            sections = all_sections.get(module_key, {})
            title = sections.get('title', module.replace('-', ' ').title())
            description = sections.get('description', 'No description available.')
            
            # Truncate description for overview
            short_desc = description.split('\n')[0][:200]
            if len(description) > 200:
                short_desc += "..."
            
            markdown += f"""
??? info "{title}"
    
    **Module:** `{category}/{module}`
    
    {short_desc}
    
    [View Details](./{module}.md){{ .md-button }}
    [GitHub Source](https://github.com/awslabs/idf-modules/tree/main/modules/{category}/{module}){{ .md-button .md-button--primary }}

"""
        
        return markdown
    
    def generate_main_index(self, modules: Dict[str, List[str]]) -> str:
        """Generate the main modules index page."""
        markdown = """# IDF Modules Documentation

This documentation is automatically generated from the [AWS IDF Modules](https://github.com/awslabs/idf-modules) repository.

## Module Categories

"""
        
        for category, module_list in sorted(modules.items()):
            module_count = len(module_list)
            markdown += f"""
### [{category.title()}](./{category}/index.md)

{module_count} module{'s' if module_count != 1 else ''} available

"""
        
        markdown += """
## About IDF Modules

The Industrial Data Fabric (IDF) modules are reusable infrastructure components designed to help you build data processing and analytics solutions on AWS.

---

*Last updated: Auto-generated from repository*
"""
        
        return markdown
    
    def generate_mkdocs_nav(self, modules: Dict[str, List[str]]) -> Dict:
        """Generate navigation structure for mkdocs.yml."""
        nav_modules = []
        
        for category, module_list in sorted(modules.items()):
            category_nav = {
                category.title(): [
                    {"Overview": f"modules/{category}/index.md"}
                ]
            }
            
            # Add individual module pages
            for module in sorted(module_list):
                category_nav[category.title()].append({
                    module.replace('-', ' ').title(): f"modules/{category}/{module}.md"
                })
            
            nav_modules.append(category_nav)
        
        return {
            "Modules": [
                {"Overview": "modules/index.md"},
                *nav_modules
            ]
        }
    
    def generate_documentation(self):
        """Main method to generate all documentation."""
        # Clone repository
        modules_path = self.clone_repository()
        
        # Discover modules
        print("Discovering modules...")
        modules = self.discover_modules(modules_path)
        print(f"Found {sum(len(mods) for mods in modules.values())} modules in {len(modules)} categories")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse all README files
        print("Parsing README files...")
        all_sections = {}
        
        for category, module_list in modules.items():
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for module in module_list:
                readme_path = modules_path / category / module / "README.md"
                if readme_path.exists():
                    sections = self.parse_readme(readme_path)
                    module_key = f"{category}/{module}"
                    all_sections[module_key] = sections
                    
                    # Generate individual module page
                    module_content = self.generate_module_page(category, module, sections)
                    module_file = category_dir / f"{module}.md"
                    with open(module_file, 'w', encoding='utf-8') as f:
                        f.write(module_content)
                    
                    print(f"Generated: {module_file}")
            
            # Generate category index
            category_content = self.generate_category_index(category, module_list, all_sections)
            category_index = category_dir / "index.md"
            with open(category_index, 'w', encoding='utf-8') as f:
                f.write(category_content)
            
            print(f"Generated: {category_index}")
        
        # Generate main index
        main_content = self.generate_main_index(modules)
        main_index = self.output_dir / "index.md"
        with open(main_index, 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        print(f"Generated: {main_index}")
        
        # Generate navigation YAML
        nav_structure = self.generate_mkdocs_nav(modules)
        nav_file = self.output_dir.parent / "nav_modules.yml"
        with open(nav_file, 'w', encoding='utf-8') as f:
            yaml.dump(nav_structure, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated navigation: {nav_file}")
        
        # Cleanup
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
        
        print(f"\nDocumentation generated successfully in {self.output_dir}")
        print(f"Add the contents of {nav_file} to your mkdocs.yml nav section")

def main():
    generator = IDFDocsGenerator()
    generator.generate_documentation()

if __name__ == "__main__":
    main()
