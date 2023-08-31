HEADER = """<svg version="1.1" width="1000" height="1000"
                    xmlns="http://www.w3.org/2000/svg">"""

FOOTER = """\n</svg>"""

RADIAL_GRADIENT_SVG = """
 <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
  <stop offset="0%%" stop-color="#%s"/>
  <stop offset="50%%" stop-color="#%s"/>
  <stop offset="100%%" stop-color="#%s"/>
 </radialGradient>"""

LINEAR_GRADIENT_SVG = """
 <linearGradient id="%s" x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" gradientUnits="userSpaceOnUse">
  <stop offset="0%%" stop-color="#454545" />
  <stop offset="25%%" stop-color="#606060" />
  <stop offset="50%%" stop-color="#454545" />
  <stop offset="100%%" stop-color="#252525" />
 </linearGradient>"""

OFFSET_X = 500
OFFSET_Y = 500