import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'image_detail_page.dart';

class UnauthorizedPage extends StatefulWidget {
  final DateTime selectedDate;

  const UnauthorizedPage({super.key, required this.selectedDate});

  @override
  _UnauthorizedPageState createState() => _UnauthorizedPageState();
}

class _UnauthorizedPageState extends State<UnauthorizedPage> {
  List<dynamic> logs = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchLogs();
  }

  Future<void> fetchLogs() async {
    final String selectedDate = widget.selectedDate.toIso8601String().split('T')[0];
    final String apiUrl = 'http://192.168.8.108:5000/logs?date=$selectedDate';

    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        setState(() {
          logs = data;
          isLoading = false;
        });
      } else {
        print("Failed to fetch logs: ${response.statusCode}");
      }
    } catch (e) {
      print("Error fetching logs: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Unauthorized Entries (${widget.selectedDate.toLocal().toString().split(' ')[0]})'),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : logs.isEmpty
              ? const Center(child: Text('No unauthorized entries found for this date.'))
              : Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        'Total Unauthorized Entries: ${logs.length}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Expanded(
                      child: ListView.builder(
                        itemCount: logs.length,
                        itemBuilder: (context, index) {
                          final log = logs[index];
                          final imageBase64 = log['image'];
                          final imageBytes = imageBase64 != null ? base64Decode(imageBase64) : null;

                          return Card(
                            child: ListTile(
                              leading: SizedBox(
                                height: 50,
                                width: 50,
                                child: imageBytes != null
                                    ? Image.memory(
                                        imageBytes,
                                        fit: BoxFit.cover,
                                      )
                                    : const Icon(Icons.image_not_supported),
                              ),
                              title: Text('Name: ${log['name']}'),
                              subtitle: Text('Time: ${log['timestamp']}'),
                              onTap: () {
                                if (imageBytes != null) {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => ImageDetailPage(
                                        imageBytes: imageBytes,
                                        name: log['name'],
                                        timestamp: log['timestamp'], imageBase64:imageBase64,
                                      ),
                                    ),
                                  );
                                } else {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('No image available for this entry'),
                                      duration: Duration(seconds: 2),
                                    ),
                                  );
                                }
                              },
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
    );
  }
}
