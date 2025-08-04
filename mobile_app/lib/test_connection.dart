import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(TestApp());
}

class TestApp extends StatefulWidget {
  const TestApp({super.key});

  @override
  _TestAppState createState() => _TestAppState();
}

class _TestAppState extends State<TestApp> {
  String _result = "Naciśnij przycisk aby przetestować połączenie";
  bool _testing = false;

  Future<void> _testConnection() async {
    setState(() {
      _testing = true;
      _result = "Testuję połączenie...";
    });

    try {
      // Test z localhost
      final response1 = await http
          .get(
            Uri.parse('http://127.0.0.1:8000/workers'),
            headers: {'Accept': 'application/json'},
          )
          .timeout(Duration(seconds: 5));

      if (response1.statusCode == 200) {
        setState(() {
          _result = "✅ Połączenie z localhost OK: ${response1.statusCode}";
        });
        return;
      }
    } catch (e) {
      print("Localhost error: $e");
    }

    try {
      // Test z IP sieci
      final response2 = await http
          .get(
            Uri.parse('http://192.168.1.30:8000/workers'),
            headers: {'Accept': 'application/json'},
          )
          .timeout(Duration(seconds: 5));

      if (response2.statusCode == 200) {
        setState(() {
          _result = "✅ Połączenie z 192.168.1.30 OK: ${response2.statusCode}";
        });
        return;
      }
    } catch (e) {
      setState(() {
        _result = "❌ Błąd połączenia z serwerem: $e";
      });
    }

    setState(() {
      _testing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Test Połączenia')),
        body: Padding(
          padding: EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(_result, textAlign: TextAlign.center),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _testing ? null : _testConnection,
                child: Text(_testing ? 'Testuję...' : 'Test Połączenia'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
