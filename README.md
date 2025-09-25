# 🔄 AIStudio to OpenWebUI Chat Converter

A Python script to convert Google AI Studio chat exports to OpenWebUI format for seamless migration between platforms.

## 🚀 Features

- **Batch Conversion**: Convert multiple AIStudio chats at once
- **Thought Process Preservation**: Embeds AI reasoning within responses using `<details>` tags
- **Filename-Based Titles**: Uses original filenames as chat titles
- **Sequential Timestamps**: Maintains message order with proper timestamps
- **Cross-Platform Compatibility**: Works with files with or without `.json` extensions

## 📋 Prerequisites

- Python 3.6+
- No additional dependencies required

## 🛠️ Usage

### Single File Conversion
```bash
python convert_aistudio_to_openwebui.py input_file output_file
```

### Batch Conversion
```bash
python convert_aistudio_to_openwebui.py input_directory output_directory --batch
```

## ⚠️ Limitations

⚠️ **Note**: While this script successfully converts chat content, there are some limitations:

- **Sorting**: Message sorting in OpenWebUI may not be perfect in all cases
- **Images**: Image attachments are not currently supported and will be lost in conversion
- **Advanced Formatting**: Some complex formatting may not translate perfectly

## 📁 Output Format

The script generates OpenWebUI-compatible JSON files that preserve:
- Conversation flow and structure
- AI reasoning/thought processes
- Message timestamps for proper ordering
- Model information and metadata

## 🤝 Contributing

This script is provided as-is for the community. Feel free to fork and improve!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgements

Special thanks to the OpenWebUI and Google AI Studio communities for their excellent tools that make this kind of interoperability possible.

---
*Happy to share this script with anyone who finds it useful! 🎉*