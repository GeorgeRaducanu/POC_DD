#include "dd_canvas/ppm_writer.hpp"

#include "dd_canvas/canvas.hpp"

#include <fstream>
#include <ostream>

namespace dd_canvas {

bool PpmWriter::write(const Canvas& canvas, const std::string& path) {
    std::ofstream output(path.c_str(), std::ios::binary);
    return output.good() && write(canvas, output);
}

bool PpmWriter::write(const Canvas& canvas, std::ostream& output) {
    output << "P6\n" << canvas.width() << ' ' << canvas.height() << "\n255\n";
    for (std::size_t y = 0; y < canvas.height(); ++y) {
        for (std::size_t x = 0; x < canvas.width(); ++x) {
            const Color color = canvas.pixel(Point{x, y});
            output.put(static_cast<char>(color.red));
            output.put(static_cast<char>(color.green));
            output.put(static_cast<char>(color.blue));
        }
    }
    return output.good();
}

}  // namespace dd_canvas
