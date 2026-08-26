#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace dd_canvas {

/**
 * @brief An immutable RGB color value.
 */
struct Color {
    std::uint8_t red;
    std::uint8_t green;
    std::uint8_t blue;

    /** @brief Creates a black color. */
    Color();

    /** @brief Creates a color from three 8-bit channels. */
    Color(std::uint8_t red_value, std::uint8_t green_value, std::uint8_t blue_value);

    /** @brief Compares all channels for equality. */
    bool operator==(const Color& other) const;
};

/**
 * @brief A two-dimensional integer coordinate.
 */
struct Point {
    std::size_t x;
    std::size_t y;
};

/**
 * @brief A compact row-major RGB raster.
 *
 * Coordinates use an origin in the upper-left corner. Pixel access is
 * bounds-checked and throws std::out_of_range when a coordinate is invalid.
 */
class Canvas {
public:
    /** @brief Creates a canvas filled with the supplied color. */
    Canvas(std::size_t width, std::size_t height, Color fill = Color());

    /** @brief Returns the canvas width in pixels. */
    std::size_t width() const;

    /** @brief Returns the canvas height in pixels. */
    std::size_t height() const;

    /** @brief Returns the pixel at a coordinate. */
    Color pixel(Point point) const;

    /** @brief Replaces the pixel at a coordinate. */
    void set_pixel(Point point, Color color);

    /** @brief Fills the entire raster with one color. */
    void fill(Color color);

    /** @brief Draws an inclusive, axis-aligned rectangle outline. */
    void draw_rectangle(Point top_left, Point bottom_right, Color color);

private:
    std::size_t index(Point point) const;

    std::size_t width_;
    std::size_t height_;
    std::vector<Color> pixels_;
};

}  // namespace dd_canvas
