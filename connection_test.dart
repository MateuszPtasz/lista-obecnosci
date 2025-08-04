// Skrypt do sprawdzania komunikacji z serwerem API
import 'dart:convert';
import 'package:http/http.dart' as http;

// Lista serwerów do sprawdzenia
List<String> servers = [
  'http://192.168.1.30:8000',
  'http://192.168.1.30:8002',
  'http://localhost:8000',
  'http://localhost:8002',
];

// Lista endpointów do sprawdzenia
List<String> endpoints = [
  '/api/connection-test',
  '/api/app-version',
  '/api/mobile-config',
  '/api/workers',
];

Future<void> main() async {
  print('====================================');
  print('DIAGNOSTYKA POŁĄCZENIA Z SERWEREM');
  print('====================================');

  for (var server in servers) {
    print('\nTestuję serwer: $server');
    print('------------------------------------');

    // Sprawdź podstawowe połączenie
    try {
      final response = await http
          .get(Uri.parse(server))
          .timeout(Duration(seconds: 3));
      print('Połączenie podstawowe: ${response.statusCode}');
    } catch (e) {
      print('❌ Błąd połączenia: $e');
      continue; // Przejdź do następnego serwera
    }

    // Sprawdź każdy endpoint
    for (var endpoint in endpoints) {
      try {
        final url = Uri.parse('$server$endpoint');
        print('\nTestuję endpoint: $endpoint');

        final response = await http.get(url).timeout(Duration(seconds: 3));

        print('Status: ${response.statusCode}');

        if (response.statusCode == 200) {
          // Pokaż tylko fragment odpowiedzi
          final body = json.decode(response.body);
          print('Odpowiedź: ${_formatResponsePreview(body)}');
        } else {
          print('Treść błędu: ${response.body}');
        }
      } catch (e) {
        print('❌ Błąd: $e');
      }
    }
  }

  print('\n====================================');
  print('ZAKOŃCZONO DIAGNOSTYKĘ');
  print('====================================');
}

String _formatResponsePreview(dynamic data) {
  if (data is Map) {
    // Pokaż tylko kluczy na najwyższym poziomie
    return '{${data.keys.join(', ')}}';
  } else if (data is List) {
    return '${data.length} elementów';
  } else {
    return data.toString();
  }
}
