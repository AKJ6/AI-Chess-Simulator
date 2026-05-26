import os

pieces = {
    'pawn': '♟',
    'knight': '♞',
    'bishop': '♝',
    'rook': '♜',
    'queen': '♛',
    'king': '♚'
}

svg_template = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <text x="50" y="75" font-size="80" text-anchor="middle" fill="{color}">{symbol}</text>
</svg>"""

for color, fill in [('white', '#ffffff'), ('black', '#000000')]:
    os.makedirs(f'assets/{color}_pieces', exist_ok=True)
    for name, symbol in pieces.items():
        with open(f'assets/{color}_pieces/{name}.svg', 'w') as f:
            # We add a small stroke to make white pieces visible on light squares
            stroke = 'stroke="black" stroke-width="2"' if color == 'white' else ''
            svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <text x="50" y="80" font-size="80" text-anchor="middle" fill="{fill}" {stroke}>{symbol}</text>
</svg>"""
            f.write(svg_content)

print("SVGs generated.")
