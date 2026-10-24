"""Explicit iris-indigo SVG palettes; no filters or visited-link CSS."""
import re
LIGHT = {
 '#131119':'#f7f8ff', '#49375f':'#d8c6e8', '#393047':'#ded2e9',
 '#bd93f9':'#5047a8', '#f1edf7':'#20263d', '#c8c0d5':'#4e405e',
 '#a79bb7':'#62516e', '#1c1528':'#edf0fc', '#624b7d':'#cbb5df',
 '#d6c9e8':'#4f3b63', '#9e75d6':'#ad8ac8', '#9d61e8':'#b386dc',
 '#c4a1ff':'#69399c', '#f4edff':'#2b1b3c', '#a897bd':'#665576',
 '#77549f':'#b99bce', '#754e9c':'#8359a5', '#a77ad7':'#9e75be',
 '#d5b3ff':'#bfa0d8', '#191320':'#eef1fb', '#664480':'#bda4d1',
 '#a779d6':'#7c4aa8', '#bc91ee':'#8351ae', '#d9b6ff':'#6e3d9e',
 '#b98ae9':'#75449e', '#e3d6f3':'#362044', '#d3aaff':'#8e5db5',
 '#2b223a':'#e9def3', '#67458b':'#cfb6e5', '#9767c7':'#b68cd5',
 '#c197f0':'#9363ba', '#e7caff':'#724499', '#211a2c':'#ddd0e9',
 '#432c62':'#b99ccf', '#614080':'#9d74bc', '#8057a4':'#7a4b9e',
 '#a97ad0':'#5a327e', '#191420':'#d1c0df', '#322044':'#a88bbf',
 '#49305e':'#8863a5', '#63417e':'#693f8a', '#80539f':'#4a2567',
 '#d3b0ff':'#8151b1'
}

# Source colours stay stable in the renderer; both output palettes are explicit.
DARK = {
 '#131119':'#10121f', '#49375f':'#343e64', '#393047':'#2e3655',
 '#bd93f9':'#a4b0ff', '#f1edf7':'#edf1ff', '#c8c0d5':'#bdc7e0',
 '#a79bb7':'#929fbe', '#1c1528':'#181d31', '#624b7d':'#454e7c',
 '#d6c9e8':'#c3cceb', '#9e75d6':'#6574b1', '#9d61e8':'#7b79d9',
 '#c4a1ff':'#b9c2ff', '#f4edff':'#eef1ff', '#a897bd':'#94a1c6',
 '#77549f':'#566199', '#754e9c':'#545994', '#a77ad7':'#8794d9',
 '#d5b3ff':'#c2ccff', '#191320':'#151a2b', '#664480':'#414a75',
 '#a779d6':'#8290cb', '#bc91ee':'#a9b7f3', '#d9b6ff':'#cbd3ff',
 '#b98ae9':'#a0ace8', '#e3d6f3':'#dbe2fa', '#d3aaff':'#b4c1ff',
 '#2b223a':'#252e4c', '#67458b':'#46578f', '#9767c7':'#6a7bb7',
 '#c197f0':'#98a7e5', '#e7caff':'#ccd5ff', '#211a2c':'#1b233b',
 '#432c62':'#303f6e', '#614080':'#4c5f98', '#8057a4':'#6f80b7',
 '#a97ad0':'#91a0d3', '#191420':'#151c30', '#322044':'#263556',
 '#49305e':'#3a4c79', '#63417e':'#526493', '#80539f':'#7282ad',
 '#d3b0ff':'#b6c4ff'
}

def _palette(svg, palette):
    def replace(match):
        color=match.group().lower()
        if color not in palette:
            raise ValueError('SVG palette missing a source colour: '+color)
        return palette[color]
    return re.sub(r'#[0-9a-fA-F]{6}',replace,svg)

def dark_svg(svg):
    return _palette(svg, DARK)

def light_svg(svg):
    return _palette(svg, LIGHT)
