// Plik: api_diagnostics.dart
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api.dart'; // Importujemy główny plik API

class ApiDiagnosticsPage extends StatefulWidget {
  const ApiDiagnosticsPage({Key? key}) : super(key: key);

  @override
  State<ApiDiagnosticsPage> createState() => _ApiDiagnosticsPageState();
}

class _ApiDiagnosticsPageState extends State<ApiDiagnosticsPage> {
  bool _isLoading = false;
  String _baseUrl = '';
  List<Map<String, dynamic>> _testResults = [];

  @override
  void initState() {
    super.initState();
    _baseUrl = baseUrl;
    _initializeAndRunTests();
  }

  Future<void> _initializeAndRunTests() async {
    setState(() {
      _isLoading = true;
      _testResults = [];
    });

    // Test 0: Szukanie działającego serwera
    await _runTest('Wyszukiwanie działającego serwera', () async {
      try {
        final serverUrl = await findWorkingServer();
        setState(() {
          _baseUrl = serverUrl;
        });
        return {
          'success': true,
          'message': 'Znaleziono działający serwer',
          'data': {'server_url': serverUrl},
        };
      } catch (e) {
        return {'success': false, 'message': 'Błąd wyszukiwania serwera: $e'};
      }
    });

    // Uruchom pozostałe testy
    _runTests();
  }

  Future<void> _runTests() async {
    setState(() {
      _isLoading = true;
      _testResults = [];
    });

    // Test 1: Połączenie internetowe
    await _runTest('Połączenie z internetem', () async {
      final result = await testInternetConnection();
      return result;
    });

    // Test 2: Połączenie z serwerem - podstawowy test
    await _runTest('Podstawowe połączenie z serwerem', () async {
      try {
        final url = Uri.parse('$baseUrl');
        final response = await http.get(url).timeout(Duration(seconds: 5));

        return {
          'success': response.statusCode < 400,
          'message': 'Kod odpowiedzi: ${response.statusCode}',
          'data': {'status_code': response.statusCode},
        };
      } catch (e) {
        return {'success': false, 'message': 'Błąd połączenia z serwerem: $e'};
      }
    });

    // Test 3: Połączenie z serwerem API - endpoint diagnostyczny
    await _runTest('Test diagnostyczny API', () async {
      try {
        final url = Uri.parse('$baseUrl/api/connection-test');
        final response = await http.get(url).timeout(Duration(seconds: 5));

        if (response.statusCode == 200) {
          return {
            'success': true,
            'message': 'Endpoint diagnostyczny działa poprawnie',
            'data': json.decode(response.body),
          };
        } else {
          return {
            'success': false,
            'message':
                'Endpoint diagnostyczny zwrócił błąd: ${response.statusCode}',
            'data': {'status_code': response.statusCode, 'body': response.body},
          };
        }
      } catch (e) {
        return {
          'success': false,
          'message': 'Błąd endpointu diagnostycznego: $e',
        };
      }
    });

    // Test 4: Pobieranie konfiguracji
    await _runTest('Pobieranie konfiguracji', () async {
      try {
        final url = Uri.parse('$baseUrl/api/mobile-config');
        final response = await http.get(url).timeout(Duration(seconds: 5));

        if (response.statusCode == 200) {
          return {
            'success': true,
            'message': 'Konfiguracja pobrana pomyślnie',
            'data': json.decode(response.body),
          };
        } else {
          return {
            'success': false,
            'message': 'Błąd pobierania konfiguracji: ${response.statusCode}',
            'data': {'status_code': response.statusCode, 'body': response.body},
          };
        }
      } catch (e) {
        return {
          'success': false,
          'message': 'Błąd podczas pobierania konfiguracji: $e',
        };
      }
    });

    // Test 5: Zapisywanie konfiguracji (test POST)
    await _runTest('Zapisywanie konfiguracji (POST)', () async {
      try {
        final url = Uri.parse('$baseUrl/api/mobile-config');
        final testData = {
          'test': true,
          'timestamp': DateTime.now().toIso8601String(),
          'device_info': 'Diagnostyka API',
        };

        final response = await http
            .post(
              url,
              headers: {'Content-Type': 'application/json'},
              body: json.encode(testData),
            )
            .timeout(Duration(seconds: 5));

        if (response.statusCode == 200) {
          return {
            'success': true,
            'message': 'Zapisywanie konfiguracji działa poprawnie',
            'data': {
              'request': testData,
              'response': json.decode(response.body),
            },
          };
        } else {
          return {
            'success': false,
            'message': 'Błąd zapisywania konfiguracji: ${response.statusCode}',
            'data': {'status_code': response.statusCode, 'body': response.body},
          };
        }
      } catch (e) {
        return {
          'success': false,
          'message': 'Błąd podczas zapisywania konfiguracji: $e',
        };
      }
    });

    // Test 6: Sprawdzanie wersji
    await _runTest('Sprawdzanie wersji aplikacji', () async {
      try {
        final url = Uri.parse('$baseUrl/api/app-version');
        final response = await http.get(url).timeout(Duration(seconds: 5));

        if (response.statusCode == 200) {
          return {
            'success': true,
            'message': 'Informacje o wersji pobrane pomyślnie',
            'data': json.decode(response.body),
          };
        } else {
          return {
            'success': false,
            'message':
                'Błąd pobierania informacji o wersji: ${response.statusCode}',
            'data': {'status_code': response.statusCode, 'body': response.body},
          };
        }
      } catch (e) {
        return {'success': false, 'message': 'Błąd połączenia: $e'};
      }
    });

    // Test 7: Sprawdzanie endpoint do pracowników
    await _runTest('Endpoint pracowników', () async {
      try {
        final url = Uri.parse('$baseUrl/api/workers');
        final response = await http.get(url).timeout(Duration(seconds: 5));

        if (response.statusCode == 200) {
          return {
            'success': true,
            'message': 'Endpoint pracowników działa poprawnie',
            'data': {
              'status_code': response.statusCode,
              'count': json.decode(response.body).length,
            },
          };
        } else {
          return {
            'success': false,
            'message': 'Błąd endpointu pracowników: ${response.statusCode}',
            'data': {'status_code': response.statusCode},
          };
        }
      } catch (e) {
        return {'success': false, 'message': 'Błąd połączenia: $e'};
      }
    });

    setState(() {
      _isLoading = false;
    });
  }

  Future<void> _runTest(
    String name,
    Future<Map<String, dynamic>> Function() test,
  ) async {
    try {
      setState(() {
        _testResults.add({
          'name': name,
          'status': 'running',
          'message': 'Uruchamianie testu...',
        });
      });

      final result = await test();
      final success = result['success'] ?? false;

      setState(() {
        _testResults.removeLast();
        _testResults.add({
          'name': name,
          'status': success ? 'success' : 'error',
          'message': result['message'] ?? 'Brak wiadomości',
          'data': result['data'],
        });
      });
    } catch (e) {
      setState(() {
        _testResults.removeLast();
        _testResults.add({
          'name': name,
          'status': 'error',
          'message': 'Wyjątek: $e',
        });
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Diagnostyka API'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _isLoading ? null : _runTests,
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            color: Colors.blueGrey[50],
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Serwer API:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(_baseUrl),
                SizedBox(height: 8),
                Text(
                  'Status połączenia:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  _isLoading
                      ? 'Testowanie...'
                      : _testResults.any((t) => t['status'] == 'error')
                      ? 'Wystąpiły problemy'
                      : 'Wszystko działa poprawnie',
                ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading && _testResults.isEmpty
                ? Center(child: CircularProgressIndicator())
                : ListView.builder(
                    itemCount: _testResults.length,
                    itemBuilder: (context, index) {
                      final test = _testResults[index];
                      return _buildTestResultTile(test);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildTestResultTile(Map<String, dynamic> test) {
    IconData icon;
    Color color;

    switch (test['status']) {
      case 'running':
        icon = Icons.pending;
        color = Colors.blue;
        break;
      case 'success':
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case 'error':
        icon = Icons.error;
        color = Colors.red;
        break;
      default:
        icon = Icons.help;
        color = Colors.grey;
    }

    return ExpansionTile(
      leading: Icon(icon, color: color),
      title: Text(test['name']),
      subtitle: Text(test['message']),
      children: [
        if (test['data'] != null)
          Padding(
            padding: EdgeInsets.all(16),
            child: Text(
              _formatJson(test['data']),
              style: TextStyle(fontFamily: 'monospace', fontSize: 12),
            ),
          ),
      ],
    );
  }

  String _formatJson(dynamic json) {
    if (json == null) return 'null';
    const encoder = JsonEncoder.withIndent('  ');
    try {
      return encoder.convert(json);
    } catch (e) {
      return json.toString();
    }
  }
}
