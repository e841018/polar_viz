# author: Tzu-Hsu Yu d09922024@ntu.etu.tw 2023/03/10

import numpy as np, cv2
import matplotlib.pyplot as plt

R = 256
r = 205
pad = 10

xs = np.linspace(-1, 1, R * 2 + 1, dtype=np.float32)
ys = np.linspace(1, -1, R * 2 + 1, dtype=np.float32)
X, Y = np.meshgrid(xs, ys)
angle = np.arctan2(Y, X) * (180 / np.pi) % 360 # [0, 360)

hue = angle * 2 % 360
saturation = np.sqrt(X**2 + Y**2)
saturation[saturation > 1] = 0
value = np.ones_like(X)
hsv = cv2.merge([hue, saturation, value])
img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
img = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(1, 1, 1))

plt.figure(figsize=(4, 4), dpi=100, constrained_layout=True)
plt.axis('off')
plt.imshow(img)
x = pad + R
y = pad + R
plt.plot(x, y, 'ko')
plt.annotate('DoLP=0\n\nAoLP=any', (pad + R, pad + R), ha='center', va='center')
for a in range(0, 180, 30):
    x = pad + R + np.cos(-a / 180 * np.pi) * R
    y = pad + R + np.sin(-a / 180 * np.pi) * R
    plt.plot(x, y, 'ko')
    x = pad + R + np.cos(-a / 180 * np.pi) * r
    y = pad + R + np.sin(-a / 180 * np.pi) * r
    plt.annotate(f'DoLP=1\nAoLP={a}$^\circ$', (x, y), ha='center', va='center')
plt.annotate('Intensity=1', (0, 0), ha='left', va='top')
plt.savefig('color_ring.png')
