#!/usr/bin/env python3
import pikepdf
import os

def compress_pdf_pikepdf(input_path, output_path):
    """Compress PDF using pikepdf with aggressive compression"""
    try:
        pdf = pikepdf.open(input_path)
        
        # Save with compression
        pdf.save(output_path, 
                 compress_streams=True,
                 stream_decode_level=pikepdf.StreamDecodeLevel.generalized,
                 object_stream_mode=pikepdf.ObjectStreamMode.generate,
                 recompress_flate=True,
                 linearize=True)
        
        pdf.close()
        
        # Get file sizes
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"✅ {os.path.basename(input_path)}")
        print(f"   Original: {original_size / 1024 / 1024:.2f} MB")
        print(f"   Compressed: {compressed_size / 1024 / 1024:.2f} MB")
        print(f"   Reduction: {reduction:.1f}%\n")
        
        return True
    except Exception as e:
        print(f"❌ Error compressing {input_path}: {e}")
        return False

# Compress all T&C PDFs
pdfs = ['T&C-PT.pdf', 'T&C-EN.pdf', 'T&C-FR.pdf']
static_dir = '/Users/filipepacheco/CascadeProjects/carscraping/static'

for pdf in pdfs:
    input_path = os.path.join(static_dir, pdf)
    output_path = os.path.join(static_dir, f"{pdf.replace('.pdf', '-compressed.pdf')}")
    
    if os.path.exists(input_path):
        compress_pdf_pikepdf(input_path, output_path)
    else:
        print(f"⚠️  File not found: {input_path}")

print("🎉 Compression complete!")
