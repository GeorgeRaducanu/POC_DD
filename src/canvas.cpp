#include "dd_canvas/canvas.hpp"

#include <algorithm>
#include <stdexcept>

namespace dd_canvas {

Color::Color() : red(0), green(0), blue(0) {}

Color::Color(std::uint8_t red_value, std::uint8_t green_value, std::uint8_t blue_value)
    : red(red_value), green(green_value), blue(blue_value) {}

bool Color::operator==(const Color& other) const {
    return red == other.red && green == other.green && blue == other.blue;
}

Canvas::Canvas(std::size_t width, std::size_t height, Color fill)
    : width_(width), height_(height), pixels_(width * height, fill) {
    if (width == 0 || height == 0) {
        throw std::invalid_argument("canvas dimensions must be positive");
    }
}

std::size_t Canvas::width() const { return width_; }

std::size_t Canvas::height() const { return height_; }

std::size_t Canvas::index(Point point) const {
    if (point.x >= width_ || point.y >= height_) {
        throw std::out_of_range("canvas coordinate is outside the raster");
    }
    return point.y * width_ + point.x;
}

Color Canvas::pixel(Point point) const { return pixels_[index(point)]; }

void Canvas::set_pixel(Point point, Color color) { pixels_[index(point)] = color; }

void Canvas::fill(Color color) {
    std::fill(pixels_.begin(), pixels_.end(), color);
}

void Canvas::draw_rectangle(Point top_left, Point bottom_right, Color color) {
    if (top_left.x > bottom_right.x || top_left.y > bottom_right.y) {
        throw std::invalid_argument("rectangle corners are ordered incorrectly");
    }
    for (std::size_t x = top_left.x; x <= bottom_right.x; ++x) {
        set_pixel(Point{x, top_left.y}, color);
        set_pixel(Point{x, bottom_right.y}, color);
    }
    for (std::size_t y = top_left.y; y <= bottom_right.y; ++y) {
        set_pixel(Point{top_left.x, y}, color);
        set_pixel(Point{bottom_right.x, y}, color);
    }
}

}  // namespace dd_canvas
