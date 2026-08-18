# QGIS Publishing Checklist

Before publishing to the official QGIS Python Plugin Repository:

1. Create a public source-code repository.
2. Put the same plugin source code in that repository.
3. Add the public repository URL to `metadata.txt` as `repository=`.
4. Add the repository issue tracker URL as `tracker=`.
5. Add a public project/README URL as `homepage=`.
6. Keep `LICENSE` in the plugin root.
7. Keep the plugin package under the repository size limit.
8. Do not include binaries, `.git`, `__pycache__`, or generated junk.
9. Include minimal documentation and sample data where useful.
10. Test the ZIP installation on QGIS/Windows and, ideally, Linux/macOS.
11. Increment `version` for every uploaded release.
12. Review the QGIS plugin approval requirements before submission.

Current package:
- Name: JSON Converter Studio
- Version: 1.1.2
- Author: S Mahendran
- License: GPL-2.0-or-later
- QGIS compatibility: 3.28 through 3.99
- External Python dependencies: None
- Source repository: https://github.com/mahendran0100/JSON-Converter-Studio
- Issue tracker: https://github.com/mahendran0100/JSON-Converter-Studio/issues
- Homepage/README: https://github.com/mahendran0100/JSON-Converter-Studio

Final publication checks:
- Verify GitHub source matches the release files.
- Verify GitHub Issues is enabled.
- Test installation in QGIS before upload.
- Upload only the clean plugin package ZIP to plugins.qgis.org.
