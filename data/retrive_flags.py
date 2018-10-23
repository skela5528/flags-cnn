import os
import pandas as pd
import urllib.request
import cairosvg
import PIL.Image

CSV_PATH = 'Country_Flags.csv'
SVG_DIR = 'flags_raw'
PNG_DIR = 'flags_png'
PNG_DIR_RESIZED = 'flags_png_resized'


def load_images_dir(img_dir, verbose=False):
    image_names = os.listdir(img_dir)
    image_paths = [os.path.join(img_dir, n) for n in image_names]
    images = []
    for im_path in image_paths:
        try:
            im = PIL.Image.open(im_path)
            images.append(im)
        except IOError:
            print("Not image or not exists: {}".format(im_path))
            continue
    if verbose:
        print("{} images loaded".format(len(images)))
    return images


def retrieve_to_dir(csv_path, out_dir, url_col=2, name_col=0):
    """Retrieve svg images from urls provided in csv."""
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(csv_path)
    flags_count = 0
    not_retrieved_flags = []
    print(" - Flags downloading ...")
    for index, row in df.iterrows():
        print(row)
        url = row[url_col]
        name = "{}.svg".format(row[name_col])
        out_path = os.path.join(out_dir, name)
        try:
            urllib.request.urlretrieve(url, filename=out_path)
        except urllib.error.HTTPError as error:
            print("!! ERROR during retrieve_to_dir()!! ", error)
            not_retrieved_flags.append(name)
            continue
        flags_count += 1
    print("{} flags are failed to download: {}".format(len(not_retrieved_flags), not_retrieved_flags))
    print(" - Done! {} flags are downloaded.\n\n".format(flags_count))


def convert_svg_to_png(svg_dir, png_out_dir):
    """Convert svg images to png with cairosvg."""
    os.makedirs(png_out_dir, exist_ok=True)
    svg_names = os.listdir(svg_dir)
    svg_names.sort()
    flags_count = 0
    not_converted_flags = []
    print(" - Flags SVG to PNG converting ...")
    for svg_name in svg_names:
        name = svg_name.split('.')[0]
        print(name)
        in_path = os.path.join(svg_dir, svg_name)
        out_path = os.path.join(png_out_dir, "{}.png".format(name))
        try:
            cairosvg.svg2png(url=in_path, write_to=out_path)
        except AttributeError as error:
            print(error)
            not_converted_flags.append(name)
            continue
        flags_count += 1
    print("{} flags are failed to convert: {}".format(len(not_converted_flags), not_converted_flags))
    print(" - Done! {} flags are converted.\n\n".format(flags_count))


def normalise_png_images(in_img_dir, out_img_dir, target_h=100):
    """Normalise images to have same height."""
    os.makedirs(out_img_dir, exist_ok=True)
    images = load_images_dir(in_img_dir)
    images_resized = []
    for im in images:
        orig_ratio = im.size[0] / im.size[1]
        target_size = (int(target_h * orig_ratio), target_h)
        im_resized = im.resize(target_size, PIL.Image.BICUBIC)
        images_resized.append(im_resized)
    # save images after resize
    names = [os.path.basename(im.filename) for im in images]
    for ind, im in enumerate(images_resized):
        out_path = os.path.join(out_img_dir, names[ind])
        im.save(out_path)
    print("{} images resized".format(len(images_resized)))


def main(csv_path, svg_dir, png_dir, png_dir_resized):
    retrieve_to_dir(csv_path, svg_dir)

    convert_svg_to_png(svg_dir, png_dir)

    normalise_png_images(png_dir, png_dir_resized)


if __name__ == '__main__':
    main(CSV_PATH, SVG_DIR, PNG_DIR, PNG_DIR_RESIZED)
