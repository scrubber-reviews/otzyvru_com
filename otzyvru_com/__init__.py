# -*- coding: utf-8 -*-

"""Top-level package for Otzyvru com."""

__author__ = """NMelis"""
__email__ = 'melis.zhoroev@gmail.com'
__version__ = '0.1.8'
__title__ = 'Otzyv'
__description__ = 'Otzyvru Первый независимый сайт отзывов России'
__slug_img_link__ = 'https://i.ibb.co/fDsDyQv/image.png'
__how_get_slug = """
Slug это символы после "/" (слеша) в конце url https://www.otzyvru.com/SLUG
<img src="https://i.ibb.co/fDsDyQv/image.png" alt="image" border="0">
"""

from .otzyvru_com import OtzyvruCom

provider = OtzyvruCom
