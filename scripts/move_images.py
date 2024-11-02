import os
import shutil
from pathlib import Path

def move_images():
    # Define source and destination directories
    base_dir = Path(__file__).resolve().parent.parent  # Get project root
    source_dir = base_dir / 'mediafiles' / 'uploads'
    dest_dir = base_dir / 'mediafiles' / 'post_imgs'

    print(f"\nScript starting...")
    print(f"Looking for images in: {source_dir}")
    print(f"Will move them to: {dest_dir}\n")

    if not source_dir.exists():
        print(f"ERROR: Source directory {source_dir} does not exist!")
        return

    # Create destination directory if it doesn't exist
    dest_dir.mkdir(exist_ok=True, parents=True)
    print(f"Destination directory ready: {dest_dir}")

    files_moved = 0
    files_failed = 0

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        root_path = Path(root)
        
        # Move each file
        for file in files:
            # Only move image files
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                source_file = root_path / file
                dest_file = dest_dir / file
                
                # Move the file
                try:
                    shutil.move(str(source_file), str(dest_file))
                    print(f"✓ Moved: {source_file.name}")
                    files_moved += 1
                except Exception as e:
                    print(f"✗ Error moving {source_file.name}: {e}")
                    files_failed += 1

    print(f"\nOperation complete!")
    print(f"Files moved successfully: {files_moved}")
    print(f"Files failed to move: {files_failed}")

if __name__ == "__main__":
    move_images() 