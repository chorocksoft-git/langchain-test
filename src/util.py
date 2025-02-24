import yaml
from PIL import Image, ImageOps
from langchain_core.prompts import loading
from langchain_core.prompts.base import BasePromptTemplate


def load_prompt(file_path, encoding="utf8") -> BasePromptTemplate:
    """
    파일 경로를 기반으로 프롬프트 설정을 로드합니다.

    이 함수는 주어진 파일 경로에서 YAML 형식의 프롬프트 설정을 읽어들여,
    해당 설정에 따라 프롬프트를 로드하는 기능을 수행합니다.

    Parameters:
    file_path (str): 프롬프트 설정 파일의 경로입니다.

    Returns:
    object: 로드된 프롬프트 객체를 반환합니다.
    """
    with open(file_path, "r", encoding=encoding) as f:
        config = yaml.safe_load(f)

    return loading.load_prompt_from_config(config)


def resize_and_pad_custom(input_path, output_path, target_width=1024, target_height=1024,
                          background_color=(255, 255, 255)):
    img = Image.open(input_path)

    # 원본 비율 유지하며 너비(target_width)에 맞게 리사이즈
    scale_factor = target_width / img.width
    new_height = int(img.height * scale_factor)
    resized_img = img.resize((target_width, new_height), Image.LANCZOS)

    # 높이가 부족하다면 상하에 패딩 추가
    delta_h = target_height - new_height
    top_pad = delta_h // 2
    bottom_pad = delta_h - top_pad
    padded_img = ImageOps.expand(resized_img, border=(0, top_pad, 0, bottom_pad), fill=background_color)

    padded_img.save(output_path)
