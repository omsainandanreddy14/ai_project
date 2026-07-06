import unittest
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("main_module", ROOT / "main.py")
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)


class MainAppTests(unittest.TestCase):
    def test_calculate_bmr(self):
        self.assertAlmostEqual(main_module.calculate_bmr("Male", 25, 70, 170), 1642.5)

    def test_resolve_project_path(self):
        resolved = main_module.resolve_project_path("main.py")
        self.assertEqual(resolved, ROOT / "main.py")

    def test_get_camera_backend_prefers_webrtc(self):
        original_webrtc = main_module.webrtc_streamer
        main_module.webrtc_streamer = object()
        try:
            self.assertEqual(main_module.get_camera_backend(), "webrtc")
        finally:
            main_module.webrtc_streamer = original_webrtc


if __name__ == "__main__":
    unittest.main()
