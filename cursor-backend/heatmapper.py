from PIL import Image, ImageDraw
import json

# Read messages from a JSON file
with open("messages.json", "r") as file:
    messages = json.load(file)

# Extract the maximum width and height from the messages
max_width = max(message["width"] for message in messages)
max_height = max(message["height"] for message in messages)


# Parameters for the image and rectangle
image_width, image_height = max_width, max_height  # Image dimensions
rectangle_coords = (50, 50, 150, 150)  # Rectangle coordinates (left, top, right, bottom)
rectangle_color = (255, 0, 0, 255)  # Rectangle color with transparency (RGBA)

# Create a new array to act as bins
bin_width = 10
x_bin = [0] * ((max_width // bin_width) + 1)
y_bin = [0] * ((max_height // bin_width) + 1)

# Count how many pixels are in each bin
for message in messages:
    x_bin_index = message["x"] // bin_width
    y_bin_index = message["y"] // bin_width
    x_bin[x_bin_index] += 1
    y_bin[y_bin_index] += 1

print(x_bin, y_bin)

import sys

sys.exit()

# Create a transparent image
image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))

# Draw the rectangle on the image
draw = ImageDraw.Draw(image)
for m in messages:
    rectangle_coords = (m["x"], m["y"], m["x"] + 2, m["y"] + 2)
    draw.rectangle(rectangle_coords, fill=rectangle_color)

# Save the image to a file
file_path = "heatmap.png"
image.save(file_path)
