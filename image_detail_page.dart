import 'dart:typed_data';
import 'package:flutter/material.dart';

class ImageDetailPage extends StatelessWidget {
  final Uint8List imageBytes;
  final String name;
  final String timestamp;

  const ImageDetailPage({
    super.key,
    required this.imageBytes,
    required this.name,
    required this.timestamp, required imageBase64,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Entry Detail'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Display the name
                Text(
                  'Name: $name',
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(height: 10),
                
                // Display the timestamp
                Text(
                  'Time: $timestamp',
                  style: const TextStyle(
                    fontSize: 18,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 20),
                
                // Display the image
                ClipRRect(
                  borderRadius: BorderRadius.circular(8.0),
                  child: Image.memory(
                    imageBytes,
                    fit: BoxFit.contain,
                    width: MediaQuery.of(context).size.width * 0.9,
                    errorBuilder: (context, error, stackTrace) {
                      return Column(
                        children: const [
                          Icon(Icons.error, size: 50, color: Colors.red),
                          Text('Failed to load image', style: TextStyle(color: Colors.red)),
                        ],
                      );
                    },
                  ),
                ),
                const SizedBox(height: 20),
                
                // Add a close button for user convenience
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  icon: const Icon(Icons.close),
                  label: const Text('Close'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 20),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
