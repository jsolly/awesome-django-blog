import re
import sys
from pathlib import Path

def clean_sql_file(input_file, output_file):
    # Patterns to match different types of image URLs in the content
    patterns = [
        # Convert all django_ckeditor_5 paths to post_imgs
        (r'src="/media/django_ckeditor_5/([^"]*)"', r'src="post_imgs/\1"'),
        (r'src="https?://[^/]+/media/django_ckeditor_5/([^"]*)"', r'src="post_imgs/\1"'),
        
        # Convert direct uploads to post_imgs
        (r'src="uploads/\d{4}/\d{2}/\d{2}/([^"]*)"', r'src="post_imgs/\1"'),
        (r'src="/uploads/\d{4}/\d{2}/\d{2}/([^"]*)"', r'src="post_imgs/\1"'),
        (r'src="/media/uploads/\d{4}/\d{2}/\d{2}/([^"]*)"', r'src="post_imgs/\1"'),
        (r'src="https?://[^/]+/media/uploads/\d{4}/\d{2}/\d{2}/([^"]*)"', r'src="post_imgs/\1"'),
        
        # Clean any remaining /media/ prefixes from post_imgs paths
        (r'src="/media/(post_imgs/[^"]*)"', r'src="\1"'),
        (r'src="https?://[^/]+/media/(post_imgs/[^"]*)"', r'src="\1"'),
        
        # Convert any remaining uploads to post_imgs
        (r'src="/?uploads/([^"]*)"', r'src="post_imgs/\1"'),
        (r'src="/media/uploads/([^"]*)"', r'src="post_imgs/\1"'),
        (r'src="https?://[^/]+/media/uploads/([^"]*)"', r'src="post_imgs/\1"'),
    ]
    
    print(f"Processing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total_matches = 0
    for pattern, replacement in patterns:
        # Count matches for this pattern
        matches = re.findall(pattern, content)
        total_matches += len(matches)
        
        if matches:
            print(f"\nFound {len(matches)} URLs matching pattern: {pattern}")
            print("Sample URLs to be cleaned:")
            for url in matches[:3]:  # Show first 3 examples
                if "django_ckeditor_5" in pattern:
                    print(f"  /media/django_ckeditor_5/{url} -> post_imgs/{url}")
                elif "uploads" in pattern:
                    print(f"  uploads/{url} -> post_imgs/{url}")
                elif "http" in pattern:
                    print(f"  https://domain.com/media/post_imgs/{url} -> post_imgs/{url}")
                else:
                    print(f"  {url} -> post_imgs/{url}")
        
        # Replace the URLs
        content = re.sub(pattern, replacement, content)
    
    # Write the modified content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nProcessing complete!")
    print(f"Total URLs cleaned: {total_matches}")
    print(f"Modified SQL saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_image_urls.py <input_sql_file> [output_sql_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_cleaned{input_file.suffix}"
    
    clean_sql_file(input_file, output_file)