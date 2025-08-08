#!/usr/bin/env python3
"""
Simple runner script for the IDF documentation generator
"""

from docs_generator import DocsGenerator

def main():
    # You can customize these paths as needed
    generator = DocsGenerator(
        #repo_url="https://github.com/awslabs/idf-modules.git",
        repo_url="https://github.com/awslabs/aiops-modules.git",
        output_dir="docs/modules"  # This will create docs/modules/ in current directory
    )
    
    print("Starting documentation generation...")
    generator.generate_documentation()
    print("Done! Check the docs/modules/ directory for generated files.")

if __name__ == "__main__":
    main()
