import argparse
from os import path
import sys

import filetype
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


# 情報
SCRIPT_NAME    = "HeaderImageFramer"
SCRIPT_VERSION = (1, 0)

# 初期値
DEFAULT_CENTER_IMAGE_RESIZE_VALUE     = 75          # % 中心のヘッダー画像の倍率
DEFAULT_BACKGROUND_IMAGE_RESIZE_VALUE = 70          # % 背景のヘッダー画像の倍率
DEFAULT_LOGO_IMAGE_RESIZE_VALUE       = 15          # % ロゴの倍率

# 引数
parser = argparse.ArgumentParser(
	prog="HeaderFrameGenerator",
)
parser.add_argument("filename")
parser.add_argument("-o", "--output")
parser.add_argument("-l", "--logo")
parser.add_argument(
	"-cr", "--center_image_resize_magnification",
	default=DEFAULT_CENTER_IMAGE_RESIZE_VALUE
)
parser.add_argument(
	"-br", "--background_image_resize_magnification",
	default=DEFAULT_BACKGROUND_IMAGE_RESIZE_VALUE
)
parser.add_argument(
	"-lr", "--logo_image_resize_magnification",
	default=DEFAULT_LOGO_IMAGE_RESIZE_VALUE
)


def image_size_thumbnail(
		size: tuple[int, int],
		percentage: int
	) -> tuple[int, int]:
	"""渡された画像サイズを指定されたサイズに収まるようにリサイズする"""

	w = round(size[0] * (percentage / 100))
	h = round(size[1] * (percentage / 100))
	return (w, h)

def get_image_center_pos(
		base_image_size: tuple[int, int],
		target_image_size: tuple[int, int]
	) -> tuple[int, int]:
	"""画像の中心座標を求める"""

	w = round((base_image_size[0] / 2) - (target_image_size[0] / 2))
	h = round((base_image_size[1] / 2) - (target_image_size[1] / 2))
	return (w, h)

def crop_image(
		target_image: Image,
		percentage: int
	) -> Image:
	"""画像をクロップする"""

	# 座標の計算
	thumbnail_image_size = image_size_thumbnail(target_image.size, percentage)
	coords = [0, 0, 0, 0]
	# Left
	coords[0] = (target_image.width - thumbnail_image_size[0]) / 2
	# Right
	coords[2] = coords[0] + thumbnail_image_size[0]
	# Upper
	coords[1] = (target_image.height - thumbnail_image_size[1]) / 2
	# Lower
	coords[3] = coords[1] + thumbnail_image_size[1]

	# 画像をクロップする
	cropped_image = target_image.crop(tuple(coords))

	return cropped_image

def add_shadow(img, shadow_tone=200, blur_radius=8):
	blurred_img = np.array(img)
	blurred_img[:,:,:3] = shadow_tone

	blurred_img = Image.fromarray(np.array(blurred_img))
	blurred_img = blurred_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

	background = Image.new("RGBA", img.size, (0, 0, 0, 0))
	background.paste(blurred_img, mask=blurred_img.split()[3])
	background.paste(img, mask=img.split()[3])

	return background

def add_shadow_to_normal_image(img, shadow_tone=200, blur_radius=8):
	new_img = Image.new(
		mode="RGBA",
		size=(round((img.width * 1.5)), round((img.height * 1.5))),
		color=(0, 0, 0, 0)
	)
	new_img.paste(img, get_image_center_pos(new_img.size, new_img.size))
	return add_shadow(img=new_img, shadow_tone=shadow_tone, blur_radius=blur_radius)


if __name__ == "__main__":
	# 引数を解析
	args = parser.parse_args()

	CENTER_IMAGE_RESIZE_VALUE = args.center_image_resize_magnification
	BACKGROUND_IMAGE_RESIZE_VALUE = args.background_image_resize_magnification


	# 画像がPNG形式か判定する
	header_image_filetype = filetype.image_match(args.filename)
	if header_image_filetype.mime != "image/png":
		print(f"Error: Invalid file format - {header_image_filetype.extension} (Supported format: png)")
		sys.exit(1)

	# ヘッダー画像を読み込む
	header_image = Image.open(args.filename)
	BASE_IMAGE_SIZE = header_image.size
	# ヘッダー画像をリサイズする
	header_image.thumbnail(image_size_thumbnail(BASE_IMAGE_SIZE, CENTER_IMAGE_RESIZE_VALUE))

	# 背景用のヘッダー画像を生成
	background_header_image = crop_image(header_image, BACKGROUND_IMAGE_RESIZE_VALUE).resize(size=BASE_IMAGE_SIZE)
	# フィルター処理
	background_header_image = background_header_image.filter(ImageFilter.GaussianBlur(4))
	background_header_image = ImageEnhance.Brightness(background_header_image).enhance(0.7)

	center_header_base_image = Image.new(
		mode="RGBA",
		size=BASE_IMAGE_SIZE,
		color=(0, 0, 0, 0)
	)

	# ヘッダー画像を合成する
	center_header_base_image.paste(
		im=header_image,
		box=get_image_center_pos(center_header_base_image.size, header_image.size)
	)
	# ドロップシャドウを追加する
	center_header_base_image = add_shadow(center_header_base_image, shadow_tone=0, blur_radius=10)

	# 背景画像へ中心のヘッダー画像を合成する
	background_header_image.alpha_composite(
		im=center_header_base_image
	)
	merged_image = background_header_image

	# ロゴを合成する
	if args.logo is not None:
		# ロゴ画像を読み込む
		logo_image = Image.open(args.logo)
		# リサイズ
		logo_image.thumbnail(image_size_thumbnail(header_image.size, 15))

		# 中心位置を取得する
		logo_base_pos = get_image_center_pos(merged_image.size, logo_image.size)

		# 位置を調整する
		logo_pos = [0, 0]
		logo_pos[0] = round((logo_base_pos[0]))
		logo_pos[1] = round(logo_base_pos[1] + (header_image.height / 2))

		# ロゴを合成する
		merged_image.alpha_composite(
			im=logo_image,
			dest=tuple(logo_pos)
		)

	# 完成した画像を保存する
	if args.output is not None:
		output_filename = args.output
	else:
		output_filename = path.join(path.dirname(args.filename), path.splitext(path.basename(args.filename))[0] + "_Framed.png")

	merged_image.save(output_filename)
