"""Explicit SVG fill/stroke palette for light mode; no filters or runtime CSS."""
import re
LIGHT = {
 '#131119':'#faf7ff', '#49375f':'#d8c6e8', '#393047':'#ded2e9',
 '#bd93f9':'#6f3ca3', '#f1edf7':'#291b38', '#c8c0d5':'#4e405e',
 '#a79bb7':'#62516e', '#1c1528':'#f1e9fa', '#624b7d':'#cbb5df',
 '#d6c9e8':'#4f3b63', '#9e75d6':'#ad8ac8', '#9d61e8':'#b386dc',
 '#c4a1ff':'#69399c', '#f4edff':'#2b1b3c', '#a897bd':'#665576',
 '#77549f':'#b99bce', '#754e9c':'#8359a5', '#a77ad7':'#9e75be',
 '#d5b3ff':'#bfa0d8', '#191320':'#f1eafa', '#664480':'#bda4d1',
 '#a779d6':'#7c4aa8', '#bc91ee':'#8351ae', '#d9b6ff':'#6e3d9e',
 '#b98ae9':'#75449e', '#e3d6f3':'#362044', '#d3aaff':'#8e5db5',
 '#2b223a':'#e9def3', '#67458b':'#cfb6e5', '#9767c7':'#b68cd5',
 '#c197f0':'#9363ba', '#e7caff':'#724499', '#211a2c':'#ddd0e9',
 '#432c62':'#b99ccf', '#614080':'#9d74bc', '#8057a4':'#7a4b9e',
 '#a97ad0':'#5a327e', '#191420':'#d1c0df', '#322044':'#a88bbf',
 '#49305e':'#8863a5', '#63417e':'#693f8a', '#80539f':'#4a2567',
 '#d3b0ff':'#8151b1'
}

def light_svg(svg):
    def replace(match):
        color=match.group().lower()
        if color not in LIGHT:
            raise ValueError('Light palette missing a source colour: '+color)
        return LIGHT[color]
    return re.sub(r'#[0-9a-fA-F]{6}',replace,svg)
