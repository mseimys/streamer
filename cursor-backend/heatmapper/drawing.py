from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt

from dataclasses import dataclass


@dataclass
class CursorPoint:
    x: int
    y: int
    width: int
    height: int
    client: str


BIN_WIDTH = 15


def value_to_color(value, max_value):
    ratio = value / max_value
    # Get the RGBA color from the colormap
    color = plt.cm.plasma(ratio, alpha=max(ratio, 0.2))
    # Convert the color to a tuple of integers
    result = list(int(x * 255) for x in color)
    return tuple(result)


def regenerate_heatmap(messages: list[CursorPoint]):
    print(f"Regenerating heatmap. Message count: {len(messages)}")

    # Extract the maximum width and height from the messages
    image_width = max(message.width for message in messages) if len(messages) > 0 else 1
    image_height = max(message.height for message in messages) if len(messages) > 0 else 1

    MAX_Y = (image_height // BIN_WIDTH) + 1
    MAX_X = (image_width // BIN_WIDTH) + 1
    totals = [[0] * (MAX_Y) for _ in range(MAX_X)]

    max_count = 0
    # Count how many pixels are in each bin
    for message in messages:
        x_bin_index = message.x // BIN_WIDTH
        y_bin_index = message.y // BIN_WIDTH
        totals[x_bin_index][y_bin_index] += 1
        if totals[x_bin_index][y_bin_index] > max_count:
            max_count = totals[x_bin_index][y_bin_index]

    # Create a transparent image
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))

    # Draw the rectangle on the image
    draw = ImageDraw.Draw(image)
    for x in range(MAX_X):
        for y in range(MAX_Y):
            count = totals[x][y]
            if count == 0:
                continue
            rectangle_coords = (
                x * BIN_WIDTH,
                y * BIN_WIDTH,
                (x + 1) * BIN_WIDTH,
                (y + 1) * BIN_WIDTH,
            )
            rectangle_color = value_to_color(count, max_count)
            draw.rectangle(rectangle_coords, fill=rectangle_color)

    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=1))

    # Save the image to a file
    file_path = "heatmap.png"
    blurred_image.save(file_path)
