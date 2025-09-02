# License Documentation

This document provides comprehensive information about the licensing of VisionAI4SchoolBus and its dependencies.

## Table of Contents

- [Project License](#project-license)
- [License Summary](#license-summary)
- [Third-Party Licenses](#third-party-licenses)
- [License Compliance](#license-compliance)
- [Commercial Use](#commercial-use)
- [Contributions](#contributions)
- [License FAQ](#license-faq)
- [Contact Information](#contact-information)

## Project License

VisionAI4SchoolBus is licensed under the **MIT License**.

### Full License Text

```
MIT License

Copyright (c) 2024 VisionAI4SchoolBus Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### License File Location

The complete license text is available in the [`LICENSE`](../LICENSE) file in the project root directory.

## License Summary

### What the MIT License Allows

✅ **Commercial Use**: Use the software for commercial purposes  
✅ **Modification**: Modify the software  
✅ **Distribution**: Distribute copies of the software  
✅ **Private Use**: Use the software privately  
✅ **Sublicensing**: Grant a sublicense to modify and distribute

### What the MIT License Requires

📋 **License and Copyright Notice**: Include the original license and copyright notice in any substantial portion of the software

### What the MIT License Does NOT Provide

❌ **Warranty**: No warranty is provided  
❌ **Liability**: Authors are not liable for damages  
❌ **Trademark Rights**: No trademark rights are granted

## Third-Party Licenses

VisionAI4SchoolBus depends on various third-party libraries, each with their own licenses:

### Core Dependencies

#### Python Runtime and Standard Libraries
- **License**: Python Software Foundation License
- **Compatibility**: Compatible with MIT License
- **Usage**: Core runtime environment

#### OpenCV (cv2)
- **License**: Apache License 2.0
- **Version**: 4.8.0+
- **Compatibility**: Compatible with MIT License
- **Usage**: Computer vision operations, camera handling

#### NumPy
- **License**: BSD-3-Clause License
- **Version**: 1.24.0+
- **Compatibility**: Compatible with MIT License
- **Usage**: Numerical computations, array operations

#### PyYAML
- **License**: MIT License
- **Version**: 6.0+
- **Compatibility**: Compatible (same license)
- **Usage**: Configuration file parsing

#### paho-mqtt
- **License**: Eclipse Public License 2.0 / Eclipse Distribution License 1.0
- **Version**: 1.6.1+
- **Compatibility**: Compatible with MIT License
- **Usage**: MQTT communication

#### psutil
- **License**: BSD-3-Clause License
- **Version**: 5.9.0+
- **Compatibility**: Compatible with MIT License
- **Usage**: System resource monitoring

### Hardware-Specific Dependencies

#### Hailo Runtime Libraries
- **License**: Proprietary Hailo License
- **Compatibility**: Requires separate license agreement with Hailo
- **Usage**: AI acceleration on Hailo NPU
- **Note**: Required for hardware acceleration, optional for CPU-only mode

#### Raspberry Pi Libraries
- **License**: Various (mostly BSD/MIT compatible)
- **Compatibility**: Compatible with MIT License
- **Usage**: Hardware-specific optimizations

### Development Dependencies

#### pytest
- **License**: MIT License
- **Compatibility**: Compatible (same license)
- **Usage**: Testing framework

#### black
- **License**: MIT License
- **Compatibility**: Compatible (same license)
- **Usage**: Code formatting

#### flake8
- **License**: MIT License
- **Compatibility**: Compatible (same license)
- **Usage**: Code linting

### Optional Dependencies

#### Docker (if using containerized deployment)
- **License**: Apache License 2.0
- **Compatibility**: Compatible with MIT License
- **Usage**: Containerization platform

#### systemd
- **License**: LGPL-2.1+
- **Compatibility**: Compatible (dynamic linking)
- **Usage**: System service management

## License Compliance

### For End Users

When using VisionAI4SchoolBus, you must:

1. **Include License Notice**: Keep the LICENSE file with any distribution
2. **Preserve Copyright**: Include copyright notices in derivative works
3. **No Trademark Claims**: Don't use project trademarks without permission

### For Redistributors

When redistributing VisionAI4SchoolBus (modified or unmodified):

1. **Include Original License**: Distribute the original LICENSE file
2. **Include Copyright Notice**: Preserve all copyright notices
3. **Document Changes**: Clearly mark any modifications made
4. **Include Third-Party Licenses**: Distribute licenses for all dependencies

### For Commercial Users

The MIT license permits commercial use without royalties, but:

1. **Include License**: Include LICENSE file in commercial distributions
2. **No Warranty**: Accept that software is provided "as is"
3. **Hailo Dependencies**: Obtain separate license for Hailo runtime if needed
4. **Compliance**: Ensure compliance with all third-party licenses

### Code Attribution Example

When including VisionAI4SchoolBus code in your project:

```python
# This file contains code from VisionAI4SchoolBus
# Original project: https://github.com/msasikumar/visionAI4schoolbus
# License: MIT License (see LICENSE file)
# Copyright (c) 2024 VisionAI4SchoolBus Contributors
```

## Commercial Use

### Permitted Commercial Activities

✅ **Integration**: Integrate into commercial products  
✅ **Service Offering**: Offer as a commercial service  
✅ **Modification**: Create commercial derivatives  
✅ **Resale**: Sell modified or unmodified versions  
✅ **Consulting**: Provide commercial consulting services  

### Commercial License Considerations

- **No Additional Fees**: MIT license requires no royalties or fees
- **Support**: No official commercial support is provided
- **Liability**: Commercial users assume all liability
- **Trademarks**: Separate permission required for trademark use

### Enterprise Deployment

For enterprise deployments:

1. **License Compliance**: Ensure all teams understand license terms
2. **Dependency Management**: Track all third-party license obligations
3. **Legal Review**: Have legal team review license implications
4. **Documentation**: Document license compliance procedures

## Contributions

### Contributor License

By contributing to VisionAI4SchoolBus, contributors agree that:

1. **License Grant**: Contributions are licensed under the same MIT License
2. **Copyright**: Contributors retain copyright to their contributions
3. **Representation**: Contributors represent they have the right to make contributions
4. **No Additional Terms**: No additional license terms apply to contributions

### Copyright Attribution

Contributors are attributed in:
- Git commit history
- [`CONTRIBUTORS.md`](contributors.md) file (if maintained)
- Release notes and documentation

### Third-Party Code

When contributing code from other sources:

1. **License Compatibility**: Ensure license is MIT-compatible
2. **Attribution**: Include proper attribution and license notices
3. **Documentation**: Document the source and license in commit messages
4. **Review**: Have contributions reviewed for license compliance

## License FAQ

### General Questions

**Q: Can I use VisionAI4SchoolBus in my commercial product?**
A: Yes, the MIT license permits commercial use without restrictions.

**Q: Do I need to pay royalties?**
A: No, the MIT license does not require royalties or licensing fees.

**Q: Can I modify the source code?**
A: Yes, you can modify the code for any purpose.

**Q: Do I need to open-source my modifications?**
A: No, the MIT license does not require you to open-source derivatives.

### Distribution Questions

**Q: What do I need to include when distributing the software?**
A: You must include the original LICENSE file and copyright notice.

**Q: Can I distribute without source code?**
A: Yes, the MIT license permits binary-only distribution.

**Q: Can I change the license of my derivative work?**
A: You can license your additions under different terms, but the original code remains MIT licensed.

### Liability Questions

**Q: What warranty is provided?**
A: None. The software is provided "as is" without any warranty.

**Q: Who is liable if the software causes damage?**
A: The license disclaims all liability. Users assume all risks.

**Q: Can I get support for the software?**
A: Community support is available, but no official support is guaranteed.

### Hailo-Specific Questions

**Q: Do I need a separate license for Hailo runtime?**
A: Yes, Hailo runtime requires a separate license agreement with Hailo.

**Q: Can I use the software without Hailo hardware?**
A: Yes, CPU-only mode is available (though with reduced performance).

**Q: What if Hailo runtime license conflicts with MIT license?**
A: You must comply with both licenses; consider CPU-only mode if needed.

## License Compatibility Matrix

| License | Compatible | Notes |
|---------|------------|-------|
| MIT | ✅ Yes | Same license |
| BSD-2-Clause | ✅ Yes | Permissive license |
| BSD-3-Clause | ✅ Yes | Permissive license |
| Apache-2.0 | ✅ Yes | Compatible permissive |
| GPL-2.0 | ⚠️ Conditional | May require GPL licensing of derivatives |
| GPL-3.0 | ⚠️ Conditional | May require GPL licensing of derivatives |
| LGPL | ✅ Yes | With dynamic linking |
| Proprietary | ⚠️ Varies | Case-by-case review required |

## Trademark Policy

### Project Name and Logo

- **"VisionAI4SchoolBus"** is a project identifier
- No formal trademark registration claimed
- Community use encouraged for project purposes
- Commercial trademark use requires permission

### Usage Guidelines

**Permitted Uses:**
- Reference to the software project
- Educational and research purposes
- Community discussions and documentation

**Restricted Uses:**
- Implying official endorsement
- Commercial branding without permission
- Misleading use of project identity

## International Considerations

### Global License Recognition

The MIT License is:
- Recognized internationally
- Compatible with most jurisdictions
- Accepted by major organizations
- Standard in open-source community

### Export Control

Users should be aware of:
- Export control regulations in their jurisdiction
- Encryption and security technology restrictions
- AI/ML technology export considerations
- Hardware-specific export controls

## Contact Information

### License Questions

For questions about licensing:

1. **Check Documentation**: Review this document and the LICENSE file
2. **Search Issues**: Look for existing discussions on GitHub
3. **Open Issue**: Create a new issue for license questions
4. **Legal Counsel**: Consult your legal counsel for complex questions

### Project Maintainers

- **Project Repository**: https://github.com/msasikumar/visionAI4schoolbus
- **Issue Tracker**: https://github.com/msasikumar/visionAI4schoolbus/issues

### Legal Notice

This document provides general information about licensing but does not constitute legal advice. For legal questions, consult qualified legal counsel.

---

**Last Updated**: January 15, 2024  
**License Version**: MIT License  
**Document Version**: 1.0

For the most current license information, always refer to the [`LICENSE`](../LICENSE) file in the project repository.