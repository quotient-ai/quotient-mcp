### `amp` Directory
[Get Started with Amp](https://ampcode.com/manual#getting-started)

The `amp` directory contains configuration files for Amp integration:

#### Files Included:

- **`AGENT.md`** - Agent rules and configuration for Amp integration
- **`examples.json`** - Example configurations and usage patterns

#### Configuration:

##### Editor Extensions

Amp can be configured through settings in your Amp supported editor extension (e.g. `.vscode/settings.json`).

All settings use the `amp.` prefix.

##### CLI Configuration

The CLI configuration file location varies by operating system:

- **Windows:** `%APPDATA%\amp\settings.json`
- **macOS:** `~/.config/amp/settings.json`
- **Linux:** `~/.config/amp/settings.json`

#### Usage:

1. Copy the `AGENT.md` rule file to your project directory
2. Configure your editor settings as needed
3. The Amp integration will be available for use

## Installation

Simply copy the desired configuration files to your target project:

```bash
cp examples/amp/AGENT.md /path/to/your/project/
```