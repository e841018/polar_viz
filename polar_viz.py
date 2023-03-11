# author: Tzu-Hsu Yu d09922024@ntu.etu.tw 2023/03/09
# Visualize videos taken with FLIR BFS-U3-51S5P-C
# Some implementations are from https://github.com/elerac/polanalyser

import imageio, numpy as np, cv2

def polar_to_hsv(img):
    # Make sure shape = (H, W)
    if len(img.shape) == 3 and img.shape[2] == 3:
        img = img[:, :, 0]
    assert len(img.shape) == 2, len(img.shape)
    
    # Demosaic
    # output: list of arrays of size about (H/2, W/2), corresponding to 0, 45, 90, 135
    # cropped to blocks of size 16 for video encoding compatibility
    H, W = img.shape
    t = H % 32 // 2
    l = W % 32 // 2
    b = t + H // 32 * 32
    r = l + W // 32 * 32
    img_000 = img[t+1:b:2, l+1:r:2]
    img_045 = img[t+0:b:2, l+1:r:2]
    img_090 = img[t+0:b:2, l+0:r:2]
    img_135 = img[t+1:b:2, l+0:r:2]
    img = np.array([img_000, img_045, img_090, img_135], dtype=np.float32)

    # Convert to Stokes vector (I, Q, U, V), assuming V=0
    # See https://en.wikipedia.org/wiki/Stokes_parameters
    I = img.sum(axis=0) * 0.5
    Q = img_000.astype(np.float32) - img_090
    U = img_045.astype(np.float32) - img_135

    # Convert the Stokes vector to Intensity, DoLP and AoLP
    img_intensity = np.clip(I * (0.5 / 255), 0, 1)
    img_dolp = np.sqrt(Q ** 2 + U ** 2) / I
    img_aolp = np.mod(0.5 * np.arctan2(U, Q).astype(np.float32), np.pi)

    # Visualize in HSV color space
    h = img_aolp * (360 / np.pi) # map [0, pi) to [0, 360)
    s = img_dolp # [0, 1]
    v = img_intensity # [0, 1]
    hsv = cv2.merge([h, s, v])
    img_vis = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    img_vis = (img_vis * 255).astype(np.uint8)

    return img_vis

if __name__ == '__main__':
    import os, tqdm
    file_list = os.listdir()
    print('Select video or image file:')
    print(''.join([f'{i}\t{name}\n' for i, name in enumerate(file_list)]))
    file_name = file_list[int(input())]

    if file_name.endswith('.bmp'):
        img = imageio.imread(file_name)
        imageio.imwrite(file_name[:-4] + '_vis.png', polar_to_hsv(img))

    elif file_name.endswith('.avi'):
        reader = imageio.get_reader(file_name)
        meta = reader.get_meta_data()
        fps = meta['fps']
        duration = meta['duration']
        writer = imageio.get_writer(file_name[:-4] + '_vis.mp4', fps=fps)
        for img in tqdm.tqdm(reader, total=int(fps * duration)):
            writer.append_data(polar_to_hsv(img))
        writer.close()
        reader.close()
