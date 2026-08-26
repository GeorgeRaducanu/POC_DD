#pragma once

#include <iosfwd>
#include <string>

namespace dd_canvas {

class Canvas;

/**
 * @brief Serializes a Canvas to the portable pixmap PPM format.
 */
class PpmWriter {
public:
    /** @brief Writes a binary PPM file and returns whether it succeeded. */
    static bool write(const Canvas& canvas, const std::string& path);

    /** @brief Writes a binary PPM stream and returns whether it succeeded. */
    static bool write(const Canvas& canvas, std::ostream& output);
};

}  // namespace dd_canvas
