import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

// Automatyczne wykrywanie adresu IP
String get baseUrl {
  if (Platform.isAndroid) {
    // Dla emulatora Android
    return 'http://10.0.2.2:8002';
  } else {
    // Dla fizycznego urządzenia - podmień na swój IP
    return 'http://192.168.1.100:8002'; // ZMIEŃ NA SWÓJ IP!
  }
}

Future<Map<String, dynamic>> sendStart(String numerPracownika, double lat, double lon, DateTime czas) async {
  try {
    final url = Uri.parse('$baseUrl/start');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'employee_id': numerPracownika,
        'czas_start': czas.toIso8601String(),
        'lokalizacja_start': {'lat': lat, 'lon': lon}
      }),
    );
    
    print('START: ${response.statusCode} ${response.body}');
    
    if (response.statusCode == 200) {
      return {'success': true, 'message': 'Rozpoczęto pracę!', 'data': jsonDecode(response.body)};
    } else {
      return {'success': false, 'message': 'Błąd serwera: ${response.statusCode}'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

Future<Map<String, dynamic>> sendStop(String numerPracownika, double lat, double lon, DateTime czas) async {
  try {
    final url = Uri.parse('$baseUrl/stop');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'employee_id': numerPracownika,
        'czas_stop': czas.toIso8601String(),
        'lokalizacja_stop': {'lat': lat, 'lon': lon}
      }),
    );
    
    print('STOP: ${response.statusCode} ${response.body}');
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final duration = data['duration_min'] ?? 0;
      return {'success': true, 'message': 'Zakończono pracę! Czas: ${duration} min', 'data': data};
    } else {
      return {'success': false, 'message': 'Błąd serwera: ${response.statusCode}'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Sprawdź czy pracownik jest obecnie w pracy
Future<Map<String, dynamic>> checkWorkerStatus(String numerPracownika) async {
  try {
    final url = Uri.parse('$baseUrl/worker/$numerPracownika/status');
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(response.body)};
    } else {
      return {'success': false, 'message': 'Nie można sprawdzić statusu'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Pobierz konfigurację aplikacji z serwera
Future<Map<String, dynamic>> getMobileConfig() async {
  try {
    final url = Uri.parse('$baseUrl/mobile-config');
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      return {'success': true, 'config': jsonDecode(response.body)};
    } else {
      return {'success': false, 'message': 'Nie można pobrać konfiguracji'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Sprawdź wersję konfiguracji
Future<Map<String, dynamic>> getConfigVersion() async {
  try {
    final url = Uri.parse('$baseUrl/config-version');
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(response.body)};
    } else {
      return {'success': false, 'message': 'Nie można pobrać wersji konfiguracji'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Sprawdź dostępne aktualizacje aplikacji
Future<Map<String, dynamic>> checkForUpdates(String currentVersion) async {
  try {
    final url = Uri.parse('$baseUrl/app-version/check');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'current_version': currentVersion,
        'device_info': {
          'platform': Platform.isAndroid ? 'android' : 'ios',
          'timestamp': DateTime.now().toIso8601String(),
        }
      }),
    );
    
    if (response.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(response.body)};
    } else {
      return {'success': false, 'message': 'Nie można sprawdzić aktualizacji'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Pobierz informacje o najnowszej wersji
Future<Map<String, dynamic>> getVersionInfo() async {
  try {
    final url = Uri.parse('$baseUrl/app-version');
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(response.body)};
    } else {
      return {'success': false, 'message': 'Nie można pobrać informacji o wersji'};
    }
  } catch (e) {
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}
