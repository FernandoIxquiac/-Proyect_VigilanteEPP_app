"""Módulo gestor de iconos vectoriales SVG para Vigilante EPP.

Permite cargar, parametrizar y renderizar iconos SVG de forma local,
offline y reactiva con adaptabilidad de tamaño, color y grosor de trazo.
"""

from functools import lru_cache
from pathlib import Path
import re
import urllib.parse


ASSETS_DIR = Path("assets")


@lru_cache(maxsize=32)
def _load_raw_svg(name: str) -> str:
    """Carga el contenido en crudo de un archivo SVG ubicado en assets/.
    
    Args:
        name: Nombre del icono con o sin extensión .svg
        
    Returns:
        Cadena con el contenido XML del SVG, o cadena vacía si no existe.
    """
    clean_name = name[:-4] if name.endswith(".svg") else name
    svg_path = ASSETS_DIR / f"{clean_name}.svg"
    if svg_path.exists():
        return svg_path.read_text(encoding="utf-8").strip()
    return ""


@lru_cache(maxsize=32)
def get_svg_data_uri(name: str) -> str:
    """Genera una data-URI en formato SVG codificado para su uso directo en CSS (mask/background).

    Args:
        name: Nombre del icono con o sin extensión .svg

    Returns:
        Cadena con la data-URI (ej. 'data:image/svg+xml;utf8,<svg...>') o cadena vacía si no existe.
    """
    raw_svg = _load_raw_svg(name)
    if not raw_svg:
        return ""
    encoded = urllib.parse.quote(raw_svg)
    return f"data:image/svg+xml;utf8,{encoded}"


def get_svg_icon(
    name: str,
    size: int = 18,
    color: str = "currentColor",
    stroke_width: float = 2.0,
    extra_style: str = ""
) -> str:
    """Genera un elemento SVG inline listo para incrustar en HTML.

    Args:
        name: Nombre del archivo de icono (ej. 'shield-check', 'alert-triangle').
        size: Dimensión en píxeles (ancho y alto).
        color: Color de trazo CSS (ej. '#10B981', 'currentColor', 'var(--brand-primary)').
        stroke_width: Grosor del trazo vectorial.
        extra_style: Propiedades CSS en línea adicionales.

    Returns:
        Fragmento HTML del SVG con los atributos modificados.
    """
    raw_svg = _load_raw_svg(name)
    if not raw_svg:
        return ""

    # Reemplazo de dimensiones ancho y alto
    svg = re.sub(r'width="[^"]*"', f'width="{size}"', raw_svg, count=1)
    svg = re.sub(r'height="[^"]*"', f'height="{size}"', svg, count=1)

    # Reemplazo de color de trazo si no es el valor por defecto de archivo
    if color != "currentColor":
        svg = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', svg, count=1)

    # Reemplazo de grosor de trazo
    svg = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{stroke_width}"', svg, count=1)

    # Inyección de estilo para alineación vertical perfecta con textos
    style_parts = [
        "display: inline-flex;",
        "align-items: center;",
        "justify-content: center;",
        "vertical-align: middle;",
        "flex-shrink: 0;"
    ]
    if extra_style:
        style_parts.append(extra_style.strip())

    inline_style = " ".join(style_parts)
    svg = re.sub(r'<svg\b', f'<svg style="{inline_style}"', svg, count=1)

    return svg
