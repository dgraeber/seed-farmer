#!/usr/bin/env python3
"""
Simple runner script for the IDF documentation generator
"""

from idf_docs_generator import IDFDocsGenerator

def main():
    # You can customize these paths as needed
    generator = IDFDocsGenerator(
        repo_url="https://github.com/awslabs/idf-modules.git",
        output_dir="docs/modules"  # This will create docs/modules/ in current directory
    )
    
    print("Starting IDF documentation generation...")
    generator.generate_documentation()
    print("Done! Check the docs/modules/ directory for generated files.")

if __name__ == "__main__":
    main()
