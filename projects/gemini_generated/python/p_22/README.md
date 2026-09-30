# Password Strength Checker and Generator

This is a command-line tool for generating strong, random passwords and for analyzing the strength of existing ones.

## Features

### Password Generator
- **Secure by Default**: Uses Python's `secrets` module to ensure generated passwords are cryptographically secure.
- **Customizable**: Allows you to specify the password length and character set (uppercase, digits, symbols).

### Password Checker
- **Strength Analysis**: Provides an overall strength rating (Very Weak to Very Strong).
- **Entropy Calculation**: Measures the password's randomness in bits.
- **Common Password Detection**: Checks the password against a list of commonly used passwords. For reproducibility, the script generates its own `common_passwords.txt` file to use for this check.
- **Secure Input**: Prompts for the password without echoing it to the terminal using `getpass`.

## Usage

This tool uses only standard Python libraries, so no external packages are needed.

### To Generate a Password

Use the `generate` command. You can customize the password with optional flags.

**Generate a default 16-character password:**
```bash
python password_tool.py generate
```

**Generate a 24-character password:**
```bash
python password_tool.py generate --length 24
```

**Generate a password with only lowercase letters and numbers:**
```bash
python password_tool.py generate --no-upper --no-symbols
```

### To Check a Password

Use the `check` command. You will be prompted to securely enter the password you want to analyze.

```bash
python password_tool.py check
```

The tool will then print a detailed analysis of the password's strength.
