# VeriChain - Local OCR Document Verification System

## 🎯 Overview

VeriChain is a blockchain-based document verification system that uses **100% local OCR** - no external API dependencies! It combines PaddleOCR for text extraction with Neo X blockchain for immutable verification.

## ✨ Key Features

- **🔒 Fully Local OCR**: Uses PaddleOCR - no API keys, no external calls, works offline
- **🔗 Blockchain Verification**: Stores document hashes on Neo X Testnet
- **🎨 Smart Text Extraction**: Advanced preprocessing and pattern matching
- **📊 Database Tracking**: SQLite database for quick lookups
- **🔍 Fuzzy Matching**: Handles OCR variations gracefully

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test OCR (Optional)

```bash
# Test OCR initialization
python test_ocr.py

# Test with a certificate image
python test_ocr.py /path/to/certificate.jpg
```

### 3. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5001`

## 📁 Project Structure

```
verichain/
├── app.py                      # Main Flask application
├── local_ocr.py               # Local OCR module (PaddleOCR)
├── test_ocr.py                # OCR testing script
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
├── templates/                 # HTML templates
│   ├── index.html
│   ├── upload.html
│   ├── verify.html
│   └── history.html
├── uploads/                   # Uploaded documents
└── document_verification.db   # SQLite database
```

## 🔧 How It Works

### Upload & Issue Process

1. **Upload Certificate**: User uploads a certificate image
2. **Local OCR Extraction**: PaddleOCR extracts text from the image
   - Preprocessing: Grayscale, denoising, contrast enhancement
   - Text extraction with confidence scoring
   - Smart parsing for name and event details
3. **Hash Generation**: Creates SHA-256 hash from extracted data
4. **Blockchain Storage**: Stores hash on Neo X Testnet
5. **Database Record**: Saves details locally for quick verification

### Verification Process

1. **Upload or Enter Hash**: User uploads certificate or enters hash
2. **OCR/Hash Extraction**: Extracts details using local OCR
3. **Database Lookup**: Searches local database
4. **Blockchain Verification**: Validates against blockchain
5. **Result**: Returns verification status with blockchain proof

## 🧠 OCR Technology

### PaddleOCR Features

- **Multi-language support** (configured for English)
- **Rotation detection** for tilted documents
- **High accuracy** with deep learning models
- **GPU support** (optional, CPU works fine)
- **Completely offline** after initial model download

### Image Preprocessing

1. Grayscale conversion
2. Noise reduction (fastNlMeansDenoising)
3. Contrast enhancement (CLAHE)
4. Adaptive thresholding

### Text Parsing

Multiple regex patterns for robust extraction:
- Name patterns: "awarded to", "presented to", capitalized names
- Event patterns: "Hackathon", event names, dates
- Fallback to manual input if OCR fails

## 🌐 Blockchain Integration

- **Network**: Neo X Testnet
- **Method**: Data anchoring via transactions
- **Hash Storage**: SHA-256 in transaction data field
- **Explorer**: https://xt4scan.ngd.network

## 📝 Environment Variables

Create a `.env` file with:

```env
# Blockchain Configuration
WEB3_PROVIDER=https://neoxt4seed1.ngd.network
PRIVATE_KEY=your_private_key_here
CHAIN_ID=12227332
EXPLORER_URL=https://xt4scan.ngd.network

# Contract (optional, uses legacy method if not set)
NFT_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000

# Flask
FLASK_SECRET_KEY=your-secret-key-here
```

## 🧪 Testing

### Test OCR Functionality

```bash
python test_ocr.py path/to/test_certificate.jpg
```

### Test with Sample Certificates

1. Create a test certificate with:
   - Participant name (e.g., "John Doe")
   - Event name (e.g., "Neo X Hackathon")
2. Upload through the web interface
3. Verify the extraction results

## 🔒 Security Notes

- Private keys should be kept secure (use environment variables)
- This is a testnet implementation (not for production)
- Database is local SQLite (consider PostgreSQL for production)

## 🎨 Web Interface

- **Home**: Landing page with navigation
- **Upload**: Upload certificates and issue to blockchain
- **Verify**: Verify certificates by image or hash
- **History**: View all issued certificates

## 📦 Dependencies

### Core
- **Flask**: Web framework
- **web3**: Blockchain interaction
- **python-dotenv**: Environment management

### OCR
- **paddleocr**: Main OCR engine
- **paddlepaddle**: Deep learning framework
- **opencv-python**: Image processing
- **Pillow**: Image handling
- **numpy**: Numerical operations

### Optional
- **pytesseract**: Fallback OCR (requires system Tesseract)

## 🚧 Troubleshooting

### PaddleOCR Installation Issues

If you encounter issues:

```bash
# Try installing paddlepaddle-cpu specifically
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple

# Or use conda
conda install paddlepaddle -c paddle
```

### OCR Not Extracting Text

1. Check image quality (should be clear, high resolution)
2. Ensure text is horizontal (or enable rotation detection)
3. Try preprocessing with different parameters
4. Use manual input as fallback

### Blockchain Connection Issues

1. Verify Neo X Testnet is accessible
2. Check private key and address
3. Ensure sufficient GAS for transactions
4. Check CHAIN_ID matches network

## 🎯 Future Enhancements

- [ ] Multi-language OCR support
- [ ] Batch processing
- [ ] PDF document support
- [ ] QR code generation for certificates
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review test_ocr.py output
- Check Flask logs for errors

---

**Built with ❤️ using PaddleOCR and Neo X Blockchain**
