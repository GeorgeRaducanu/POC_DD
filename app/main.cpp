#include "dd_canvas/canvas.hpp"
#include "dd_canvas/ppm_writer.hpp"

#include <iostream>

int main() {
    dd_canvas::Canvas canvas(160, 100, dd_canvas::Color(24, 28, 36));
    canvas.draw_rectangle(dd_canvas::Point{8, 8}, dd_canvas::Point{151, 91}, dd_canvas::Color(90, 200, 180));
    canvas.draw_rectangle(dd_canvas::Point{32, 28}, dd_canvas::Point{127, 71}, dd_canvas::Color(236, 180, 72));

    const std::string output_path = "output/sample.ppm";
    if (!dd_canvas::PpmWriter::write(canvas, output_path)) {
        std::cerr << "Unable to write " << output_path << '\n';
        return 1;
    }
    std::cout << "Wrote " << output_path << '\n';
    return 0;
}
