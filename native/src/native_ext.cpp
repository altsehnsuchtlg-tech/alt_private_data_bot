#include <pybind11/pybind11.h>

#include <cstddef>
#include <cstdint>
#include <string>

namespace py = pybind11;

std::int64_t score_text(const std::string& text) {
    std::int64_t score = 0;
    for (std::size_t i = 0; i < text.size(); ++i) {
        score += static_cast<std::int64_t>(i + 1) * static_cast<unsigned char>(text[i]);
    }
    return score % 100000;
}

PYBIND11_MODULE(native_ext, m) {
    m.doc() = "Native extension for CPU-heavy logic placeholder.";
    m.def("score_text", &score_text, "Calculate a deterministic score for text input.");
}
