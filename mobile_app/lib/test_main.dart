import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(TestApp());
}

class TestApp extends StatelessWidget {
  const TestApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(title: 'Test Połączenia', home: TestPage());
  }
}

class TestPage extends StatefulWidget {
  const TestPage({super.key});

  @override
  _TestPageState createState() => _TestPageState();
}

class _TestPageState extends State<TestPage> {
  String _log = '';
  final String baseUrl = 'http://192.168.1.30:8000';

  void _addLog(String message) {
    setState(() {
      _log += '${DateTime.now().toString().substring(11, 19)}: $message\n';
    });
    print(message);
  }

  Future<void> _testConnection() async {
    _addLog('🚀 Rozpoczynam test połączenia...');

    try {
      // Test 1: Google
      _addLog('📡 Test 1: Połączenie z Google...');
      final googleResponse = await http
          .get(Uri.parse('https://www.google.com'))
          .timeout(Duration(seconds: 5));
      _addLog('✅ Google: ${googleResponse.statusCode}');
    } catch (e) {
      _addLog('❌ Google: $e');
    }

    try {
      // Test 2: Server ping
      _addLog('📡 Test 2: Ping serwera...');
      final pingResponse = await http
          .get(Uri.parse('$baseUrl/'))
          .timeout(Duration(seconds: 5));
      _addLog('✅ Server ping: ${pingResponse.statusCode}');
      _addLog('📄 Server response: ${pingResponse.body}');
    } catch (e) {
      _addLog('❌ Server ping: $e');
    }

    try {
      // Test 3: Check employee
      _addLog('📡 Test 3: Sprawdzam pracownika JAN001...');
      final empResponse = await http
          .get(Uri.parse('$baseUrl/employees/JAN001'))
          .timeout(Duration(seconds: 5));
      _addLog('✅ Employee check: ${empResponse.statusCode}');
      _addLog('📄 Employee data: ${empResponse.body}');
    } catch (e) {
      _addLog('❌ Employee check: $e');
    }

    try {
      // Test 4: Start work
      _addLog('📡 Test 4: Rozpoczynam pracę...');
      final startData = {
        'employee_id': 'JAN001',
        'czas_start': DateTime.now().toIso8601String(),
        'lokalizacja_start': {'lat': 50.0, 'lon': 20.0},
      };

      _addLog('📤 Wysyłam dane: ${json.encode(startData)}');

      final startResponse = await http
          .post(
            Uri.parse('$baseUrl/start'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(startData),
          )
          .timeout(Duration(seconds: 10));

      _addLog('✅ Start work: ${startResponse.statusCode}');
      _addLog('📄 Start response: ${startResponse.body}');
    } catch (e) {
      _addLog('❌ Start work: $e');
    }

    _addLog('🏁 Test zakończony!');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Test Połączenia')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: _testConnection,
              child: Text('Uruchom Test'),
            ),
            SizedBox(height: 20),
            Expanded(
              child: SingleChildScrollView(
                child: Text(
                  _log,
                  style: TextStyle(fontFamily: 'monospace', fontSize: 12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
