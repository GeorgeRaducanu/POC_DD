#include "dd_canvas/canvas.hpp"
#include "dd_canvas/ppm_writer.hpp"

#include <cassert>
#include <sstream>
#include <stdexcept>
#include <string>

int main() {
    const dd_canvas::Color background(10, 20, 30);
    const dd_canvas::Color accent(200, 100, 50);
    dd_canvas::Canvas canvas(4, 3, background);

    assert(canvas.width() == 4);
    assert(canvas.height() == 3);
    assert(canvas.pixel(dd_canvas::Point{2, 1}) == background);

    canvas.set_pixel(dd_canvas::Point{2, 1}, accent);
    assert(canvas.pixel(dd_canvas::Point{2, 1}) == accent);

    bool threw = false;
    try {
        canvas.pixel(dd_canvas::Point{4, 0});
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw);

    std::ostringstream output(std::ios::binary);
    assert(dd_canvas::PpmWriter::write(canvas, output));
    const std::string encoded = output.str();
    assert(encoded.compare(0, 11, "P6\n4 3\n255\n") == 0);
    assert(encoded.size() == 11 + 4 * 3 * 3);
    return 0;
}
