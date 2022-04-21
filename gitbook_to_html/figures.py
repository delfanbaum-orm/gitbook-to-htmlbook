import glob
import os
import shutil


def process_images(book_dir, out_dir):
    """
    Moves all images in the book_dir into an images/ directory
    in the out_dir
    """
    book_dir = os.path.abspath(book_dir)
    if not book_dir[-1] == "/":
        book_dir = book_dir + "/"

    out_dir = os.path.abspath(out_dir)
    if not out_dir[-1] == "/":
        out_dir = out_dir + "/"

    # ensure the images folder exists
    try:
        print("Creating images directory...")
        os.mkdir(out_dir+"images")
    except FileExistsError:
        print("Images directory already exists!")
    except FileNotFoundError:
        print("Specified out directory does not exist... exiting")
        exit()

    # get images
    image_files = glob.glob(book_dir + '**/*.png', recursive=True)
    image_files.extend(glob.glob(book_dir + '**/*.jpg', recursive=True))
    image_files.extend(glob.glob(book_dir + '**/*.jpeg', recursive=True))
    image_files.extend(glob.glob(book_dir + '**/*.svg', recursive=True))

    # copy things
    for fn in image_files:
        shutil.copy(fn, out_dir + "images/" + fn.split('/')[-1])
