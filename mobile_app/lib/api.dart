// Konfiguracja adresu IP serwera
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';

// Lista adresów IP do próbowania w kolejności
final List<String> _serverAddresses = [
  'http://192.168.1.35:8000', // Podstawowy adres IP w sieci WiFi
  'http://localhost:8000', // Localhost na porcie 8000
  'http://127.0.0.1:8000', // Loopback na porcie 8000
  'http://192.168.1.35:8002', // Zapasowy adres na porcie 8002
  'http://localhost:8002', // Localhost na porcie 8002
  'http://127.0.0.1:8002', // Loopback na porcie 8002
  'http://192.168.1.35:8080', // Alternatywny port 8080
];

Future<Map<String, dynamic>> fetchServerConfig(String url) async {
  final response = await _fetchWithRetry(Uri.parse(url), method: 'GET');

  if (response.statusCode == 200) {
    print('✅ Konfiguracja pobrana pomyślnie');
    final rawData = json.decode(response.body);
    print('📊 Otrzymane dane raw: $rawData');

    Map<String, dynamic> data;
    if (rawData is Map<String, dynamic>) {
      if (rawData.containsKey('config') &&
          rawData['config'] is Map<String, dynamic>) {
        // Stary format z zagnieżdżonym 'config'
        data = {
          'config': rawData['config'],
          'version': rawData['version'] ?? 'unknown',
          'timestamp': rawData['timestamp'] ?? DateTime.now().toIso8601String(),
        };
      } else {
        // Nowy format (flat)
        final configData = Map<String, dynamic>.from(rawData);
        final version = configData.remove('version') ?? 'unknown';
        final timestamp =
            configData.remove('timestamp') ?? DateTime.now().toIso8601String();
        final error = configData.remove('error');

        data = {
          'config': configData,
          'version': version,
          'timestamp': timestamp,
        };

        if (error != null) {
          data['error'] = error;
        }
      }

      print('📊 Przetworzone dane: $data');
      return data;
    } else {
      print('❌ Nieoczekiwany format danych: $rawData');
      return {
        'config': {'enable_location': false, 'offline_mode_enabled': true},
        'version': 'error',
        'timestamp': DateTime.now().toIso8601String(),
        'error': 'Nieoczekiwany format danych',
      };
    }
  } else {
    print('❌ Błąd HTTP: ${response.statusCode}');
    return {
      'config': {'enable_location': false, 'offline_mode_enabled': true},
      'version': 'error',
      'timestamp': DateTime.now().toIso8601String(),
      'error': 'Błąd HTTP ${response.statusCode}',
    };
  }
}

// Zapisany działający adres
String _cachedBaseUrl = '';

// Adres IP serwera dla fizycznego telefonu
String get baseUrl {
  // Jeśli mamy zapisany działający adres, używamy go
  if (_cachedBaseUrl.isNotEmpty) {
    return _cachedBaseUrl;
  }

  // W przeciwnym razie zwracamy domyślny adres
  return _serverAddresses[0];
}

// Funkcja do testowania i ustawienia działającego adresu IP
Future<String> findWorkingServer() async {
  print('🔍 Szukam działającego serwera API...');

  for (var serverUrl in _serverAddresses) {
    try {
      print('Próbuję połączyć się z: $serverUrl');
      final response = await http
          .get(Uri.parse('$serverUrl/api/connection-test'))
          .timeout(Duration(seconds: 2));

      if (response.statusCode == 200) {
        print('✅ Znaleziono działający serwer: $serverUrl');
        _cachedBaseUrl = serverUrl;
        return serverUrl;
      }
    } catch (e) {
      print('❌ Błąd połączenia z $serverUrl: $e');
    }
  }

  print('❌ Nie znaleziono działającego serwera!');
  return _serverAddresses[0]; // Zwracamy domyślny w przypadku niepowodzenia
}

// Funkcja pomocnicza do tworzenia adresów URL API
Uri buildApiUrl(String path) {
  // Upewnij się, że ścieżka zaczyna się od "/"
  if (!path.startsWith('/')) {
    path = '/$path';
  }

  // Upewnij się, że ścieżka zaczyna się od "/api/"
  if (!path.startsWith('/api/') && !path.startsWith('/api?')) {
    path = '/api$path';
  }

  return Uri.parse('$baseUrl$path');
}

// Funkcja do testowania połączenia z API przy użyciu endpointu diagnostycznego
Future<Map<String, dynamic>> testApiConnection() async {
  try {
    print('🔍 Testuję połączenie z API używając endpointu diagnostycznego...');
    final url = buildApiUrl('/connection-test');
    final response = await http.get(url).timeout(Duration(seconds: 5));

    if (response.statusCode == 200) {
      print('✅ Test API zakończony sukcesem: ${response.statusCode}');
      final responseData = json.decode(response.body);
      return {
        'success': true,
        'message': 'API działa poprawnie',
        'data': responseData,
      };
    } else {
      print('⚠️ Test API zakończony niepowodzeniem: ${response.statusCode}');
      return {
        'success': false,
        'message': 'Błąd API: ${response.statusCode}',
        'details': response.body,
      };
    }
  } catch (e) {
    print('❌ Błąd podczas testu API: $e');
    return {
      'success': false,
      'message': 'Nie można połączyć się z API',
      'details': e.toString(),
    };
  }
}

// Funkcja testowa do sprawdzenia połączenia internetowego
Future<Map<String, dynamic>> testInternetConnection() async {
  try {
    print('🌐 Testuję połączenie z Internetem...');
    final response = await http
        .get(Uri.parse('https://www.google.com'))
        .timeout(Duration(seconds: 5));
    print('🌐 Google: ${response.statusCode}');
    return {'success': true, 'message': 'Internet działa'};
  } catch (e) {
    print('❌ Brak Internetu: $e');
    return {'success': false, 'message': 'Brak połączenia z Internetem'};
  }
}

// Funkcja testowa do sprawdzenia połączenia z serwerem lokalnym
Future<Map<String, dynamic>> testServerConnection() async {
  try {
    print('🏠 Testuję połączenie z serwerem lokalnym...');
    final response = await http
        .get(Uri.parse('$baseUrl/api/workers'))
        .timeout(Duration(seconds: 5));
    print('🏠 Server: ${response.statusCode}');
    return {'success': true, 'message': 'Serwer lokalny działa'};
  } catch (e) {
    print('❌ Błąd serwera lokalnego: $e');
    return {
      'success': false,
      'message': 'Nie można połączyć z serwerem lokalnym',
    };
  }
}

// Funkcja do sprawdzenia statusu pracownika
Future<Map<String, dynamic>> checkWorkerStatus(String numerPracownika) async {
  try {
    // Probujemy najpierw nowy endpoint z większą ilością informacji
    final url = Uri.parse('$baseUrl/api/worker/$numerPracownika/status');
    final response = await _fetchWithRetry(url);

    print(
      '📱 Sprawdzanie statusu pracownika ${numerPracownika}: ${response.statusCode}',
    );
    if (response.statusCode == 200) {
      try {
        final data = json.decode(response.body);
        print('📱 Otrzymane dane statusu: $data');

        return {
          'success': true,
          'is_working': data['is_active'] ?? false,
          'name': data['name'] ?? 'Nieznany',
          'worker_id': data['worker_id'] ?? numerPracownika,
          'shift_id': data['shift_id'],
          'start_time': data['start_time'],
          'duration': data['duration'],
          'duration_minutes': data['duration_minutes'],
          'last_shift_id': data['last_shift_id'],
          'last_start_time': data['last_start_time'],
          'last_stop_time': data['last_stop_time'],
        };
      } catch (e) {
        print('❌ Błąd przetwarzania danych statusu: $e');
        return {
          'success': false,
          'message': 'Błąd przetwarzania danych: $e',
          'is_working': false,
        };
      }
    } else {
      print('❌ Błąd serwera przy sprawdzaniu statusu: ${response.statusCode}');
      return {
        'success': false,
        'message': 'Błąd serwera: ${response.statusCode}',
        'is_working': false,
      };
    }
  } catch (e) {
    print('❌ Błąd połączenia przy sprawdzaniu statusu: $e');
    return {
      'success': false,
      'message': 'Błąd połączenia: $e',
      'is_working': false,
    };
  }
}

// =============================================================================
// NOWE FUNKCJE DLA STATYSTYK Z ZABEZPIECZENIEM PIN
// =============================================================================

// Funkcja do weryfikacji PIN dla dostępu do statystyk
Future<Map<String, dynamic>> verifyPinForStatistics(
  String workerId,
  String pin, {
  String periodType = 'month',
  String? startDate,
  String? endDate,
}) async {
  try {
    // Pobierz informacje o urządzeniu
    final deviceInfo = await getDeviceInfo();

    final url = Uri.parse('$baseUrl/statistics/verify-pin');
    final requestBody = {
      'worker_id': workerId,
      'pin': pin,
      'device_info': deviceInfo,
      'location': {
        'latitude': null, // Można dodać lokalizację jeśli potrzebna
        'longitude': null,
        'location_text': 'Mobile App',
      },
      'period_type': periodType,
    };

    // Dodaj daty dla custom period
    if (periodType == 'custom' && startDate != null && endDate != null) {
      requestBody['start_date'] = startDate;
      requestBody['end_date'] = endDate;
    }

    final response = await http
        .post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: json.encode(requestBody),
        )
        .timeout(Duration(seconds: 10));

    print('PIN verification response: ${response.statusCode}');
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {
        'success': false,
        'message': 'Błąd weryfikacji PIN: ${response.statusCode}',
      };
    }
  } catch (e) {
    print('Error verifying PIN: $e');
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Funkcja do pobierania statystyk pracownika (po weryfikacji PIN)
Future<Map<String, dynamic>> getWorkerStatistics(String workerId) async {
  try {
    final url = Uri.parse('$baseUrl/statistics/worker/$workerId');
    final response = await http.get(url).timeout(Duration(seconds: 15));

    print('Statistics response: ${response.statusCode}');
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {
        'success': false,
        'message': 'Błąd pobierania statystyk: ${response.statusCode}',
      };
    }
  } catch (e) {
    print('Error fetching statistics: $e');
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Funkcja do pobierania statystyk dla określonego okresu
Future<Map<String, dynamic>> getWorkerStatisticsByPeriod(
  String workerId, {
  required String periodType,
  String? startDate,
  String? endDate,
}) async {
  try {
    final url = Uri.parse('$baseUrl/statistics/worker/$workerId/period');
    final requestBody = {'period_type': periodType};

    // Dodaj daty dla custom period
    if (periodType == 'custom' && startDate != null && endDate != null) {
      requestBody['start_date'] = startDate;
      requestBody['end_date'] = endDate;
    }

    final response = await http
        .post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: json.encode(requestBody),
        )
        .timeout(Duration(seconds: 15));

    print('Period statistics response: ${response.statusCode}');
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {
        'success': false,
        'message': 'Błąd pobierania statystyk: ${response.statusCode}',
      };
    }
  } catch (e) {
    print('Error fetching period statistics: $e');
    return {'success': false, 'message': 'Błąd połączenia: $e'};
  }
}

// Funkcja do sprawdzenia statusu pracownika (kontynuacja)
Future<Map<String, dynamic>> getWorkerInfo(String numerPracownika) async {
  try {
    final url = Uri.parse('$baseUrl/worker/$numerPracownika');
    final response = await http.get(url).timeout(Duration(seconds: 10));

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {'error': 'Błąd pobierania danych: ${response.statusCode}'};
    }
  } catch (e) {
    return {'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do wysłania danych o rozpoczęciu pracy
Future<Map<String, dynamic>> sendStart(
  String numerPracownika,
  double lat,
  double lon,
  DateTime czas,
) async {
  try {
    print('🚀 sendStart: Rozpoczynam wysyłanie danych');
    print('📍 ID: $numerPracownika');
    print('📍 Lokalizacja: $lat, $lon');
    print('📍 Czas: ${czas.toIso8601String()}');
    print('📍 URL: $baseUrl/start');

    final url = Uri.parse('$baseUrl/start');
    final requestData = {
      'employee_id': numerPracownika,
      'czas_start': czas.toIso8601String(),
      'lokalizacja_start': {'lat': lat, 'lon': lon},
    };

    print('📍 Dane żądania: $requestData');

    final response = await http
        .post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: json.encode(requestData),
        )
        .timeout(Duration(seconds: 10)); // Dodaj timeout

    print('📍 Status odpowiedzi: ${response.statusCode}');
    print('📍 Treść odpowiedzi: ${response.body}');

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data == null) {
        return {'success': false, 'error': 'Serwer zwrócił puste dane'};
      }
      // Backend zwraca {"msg": "...", "id": ...}, konwertujemy na nasz format
      return {
        'success': true,
        'message': data['msg'] ?? 'Praca rozpoczęta',
        'id': data['id'],
      };
    } else {
      return {
        'success': false,
        'error': 'Błąd serwera: ${response.statusCode}',
      };
    }
  } catch (e) {
    print('❌ sendStart ERROR: $e');
    return {'success': false, 'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do wysłania danych o zakończeniu pracy
Future<Map<String, dynamic>> sendStop(
  String numerPracownika,
  double lat,
  double lon,
  DateTime czas,
) async {
  try {
    final url = Uri.parse('$baseUrl/stop');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'employee_id': numerPracownika,
        'czas_stop': czas.toIso8601String(),
        'lokalizacja_stop': {'lat': lat, 'lon': lon},
      }),
    );

    if (response.statusCode == 200) {
      try {
        final data = json.decode(response.body);
        if (data == null) {
          return {'success': false, 'error': 'Serwer zwrócił puste dane'};
        }
        // Backend zwraca {"msg": "...", "duration_min": ...}, konwertujemy na nasz format
        return {
          'success': true,
          'message': data['msg']?.toString() ?? 'Praca zakończona',
          'duration_min': data['duration_min'],
        };
      } catch (parseError) {
        return {
          'success': false,
          'error': 'Błąd parsowania odpowiedzi: $parseError',
        };
      }
    } else {
      return {
        'success': false,
        'error': 'Błąd serwera: ${response.statusCode}',
      };
    }
  } catch (e) {
    return {'success': false, 'error': 'Błąd połączenia: $e'};
  }
}

// Stałe dla konfiguracji HTTP
const int timeoutSeconds = 10;
const int maxRetries = 3;

// Funkcja do wykonania zapytania HTTP z obsługą ponownych prób
Future<http.Response> _fetchWithRetry(
  Uri url, {
  int retries = maxRetries,
  String method = 'GET',
  Map<String, String>? headers,
  dynamic body,
}) async {
  int attempt = 0;
  Exception? lastException;

  while (attempt < retries) {
    try {
      http.Response response;

      // Dodaj domyślne nagłówki jeśli nie podano
      headers = headers ?? {};
      if (body != null && headers['Content-Type'] == null) {
        headers['Content-Type'] = 'application/json';
      }

      switch (method.toUpperCase()) {
        case 'GET':
          response = await http
              .get(url, headers: headers)
              .timeout(Duration(seconds: timeoutSeconds));
          break;
        case 'POST':
          response = await http
              .post(url, headers: headers, body: body)
              .timeout(Duration(seconds: timeoutSeconds));
          break;
        case 'PUT':
          response = await http
              .put(url, headers: headers, body: body)
              .timeout(Duration(seconds: timeoutSeconds));
          break;
        case 'DELETE':
          response = await http
              .delete(url, headers: headers, body: body)
              .timeout(Duration(seconds: timeoutSeconds));
          break;
        default:
          throw Exception('Nieobsługiwana metoda HTTP: $method');
      }

      // Logowanie statusu odpowiedzi
      print('📡 [$method] ${url.path}: ${response.statusCode}');

      // Jeśli status 401/403, zapisz informacje diagnostyczne
      if (response.statusCode == 401 || response.statusCode == 403) {
        print(
          '🔒 Błąd autoryzacji: ${response.statusCode}, body: ${response.body}',
        );
      }

      return response;
    } catch (e) {
      lastException = e as Exception;
      attempt++;
      print('❌ Próba $attempt/$retries nie powiodła się: $e');
      if (attempt < retries) {
        // Eksponencjalne opóźnienie między próbami
        await Future.delayed(Duration(seconds: attempt));
      }
    }
  }

  throw lastException!;
}

// Funkcja do pobrania konfiguracji mobilnej
Future<Map<String, dynamic>> getMobileConfig() async {
  try {
    final url = buildApiUrl(
      '/api/mobile-config',
    ); // Używamy nowej funkcji pomocniczej z prawidłowym endpointem /api/
    print('📱 Pobieranie konfiguracji z: $url');

    final response = await _fetchWithRetry(url, method: 'GET');

    if (response.statusCode == 200) {
      print('✅ Konfiguracja pobrana pomyślnie');
      final data = json.decode(response.body);
      print('📊 Otrzymane dane: $data');
      return data;
    } else {
      print(
        '⚠️ Błąd pobierania konfiguracji: ${response.statusCode}, body: ${response.body}',
      );
      // Domyślna konfiguracja w przypadku błędu
      return {
        'error': 'Błąd pobierania konfiguracji: ${response.statusCode}',
        'config': {'enable_location': false, 'offline_mode_enabled': true},
        'version': 'error',
        'timestamp': DateTime.now().toIso8601String(),
      };
    }
  } catch (e) {
    print('❌ Błąd połączenia: $e');
    // Domyślna konfiguracja w przypadku błędu połączenia
    return {
      'error': 'Błąd połączenia: $e',
      'config': {'enable_location': false, 'offline_mode_enabled': true},
      'version': 'error',
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
}

// Funkcja do zapisywania konfiguracji mobilnej
Future<Map<String, dynamic>> saveMobileConfig(
  Map<String, dynamic> config,
) async {
  try {
    final url = buildApiUrl(
      '/api/mobile-config',
    ); // Używamy nowej funkcji pomocniczej z prawidłowym endpointem /api/
    print('📱 Zapisywanie konfiguracji do: $url');
    print('📱 Dane konfiguracji: $config');

    final response = await _fetchWithRetry(
      url,
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: json.encode(config),
    );

    if (response.statusCode == 200) {
      print('✅ Konfiguracja zapisana pomyślnie');
      return json.decode(response.body);
    } else {
      print(
        '⚠️ Błąd zapisywania konfiguracji: ${response.statusCode}, ${response.body}',
      );
      return {
        'error': 'Błąd zapisywania konfiguracji: ${response.statusCode}',
        'status': 'error',
        'message': 'Nie udało się zapisać konfiguracji',
      };
    }
  } catch (e) {
    print('❌ Błąd połączenia przy zapisywaniu konfiguracji: $e');
    return {
      'error': 'Błąd połączenia: $e',
      'status': 'error',
      'message': 'Błąd połączenia przy zapisywaniu konfiguracji',
    };
  }
}

// Funkcja do sprawdzenia aktualizacji
Future<Map<String, dynamic>> checkForUpdates(String currentVersion) async {
  try {
    final url = Uri.parse('$baseUrl/api/app-version/check');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'current_version': currentVersion}),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {'error': 'Błąd sprawdzania aktualizacji: ${response.statusCode}'};
    }
  } catch (e) {
    return {'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do pobrania informacji o wersji
Future<Map<String, dynamic>> getVersionInfo() async {
  try {
    final url = buildApiUrl(
      '/app-version',
    ); // Używamy nowej funkcji pomocniczej
    final response = await _fetchWithRetry(url, method: 'GET');

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      print('📊 Informacje o wersji: $data');
      return data;
    } else {
      print(
        '⚠️ Błąd pobierania informacji o wersji: ${response.statusCode}, ${response.body}',
      );
      return {
        'error': 'Błąd pobierania informacji o wersji: ${response.statusCode}',
        'version': 'error',
        'build': 'unknown',
        'timestamp': DateTime.now().toIso8601String(),
      };
    }
  } catch (e) {
    print('❌ Błąd połączenia przy pobieraniu wersji: $e');
    return {
      'error': 'Błąd połączenia: $e',
      'version': 'error',
      'build': 'unknown',
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
}

// Funkcja do pobrania statystyk pracownika
Future<Map<String, dynamic>> getWorkerStats(String workerId) async {
  try {
    final url = Uri.parse('$baseUrl/worker/$workerId/stats');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {'error': 'Błąd pobierania statystyk: ${response.statusCode}'};
    }
  } catch (e) {
    return {'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do sprawdzenia czy pracownik istnieje (bez PIN-a)
Future<Map<String, dynamic>> checkEmployee(String employeeId) async {
  try {
    print('🔍 checkEmployee: Sprawdzam ID $employeeId');
    final url = Uri.parse('$baseUrl/employees/$employeeId');
    print('🔍 URL: $url');

    final response = await http.get(url).timeout(Duration(seconds: 5));

    print('🔍 Status: ${response.statusCode}');
    print('🔍 Response: ${response.body}');

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return {
        'success': true,
        'employee_id': data['id'],
        'name': data['name'],
        'message': 'Pracownik znaleziony',
      };
    } else if (response.statusCode == 404) {
      return {'success': false, 'message': 'Pracownik nie znaleziony'};
    } else {
      return {'error': 'Błąd sprawdzania pracownika: ${response.statusCode}'};
    }
  } catch (e) {
    print('❌ checkEmployee ERROR: $e');
    return {'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do logowania pracownika z PIN-em
Future<Map<String, dynamic>> loginEmployee(
  String employeeId,
  String pin,
) async {
  try {
    final url = Uri.parse('$baseUrl/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'employee_id': employeeId, 'pin': pin}),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {'error': 'Błąd logowania: ${response.statusCode}'};
    }
  } catch (e) {
    return {'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do weryfikacji PIN-u
Future<Map<String, dynamic>> verifyPin(String employeeId, String pin) async {
  try {
    final url = Uri.parse('$baseUrl/verify-pin');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'employee_id': employeeId, 'pin': pin}),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {'error': 'Błąd weryfikacji PIN: ${response.statusCode}'};
    }
  } catch (e) {
    return {'error': 'Błąd połączenia: $e'};
  }
}

// Funkcja do zbierania informacji o urządzeniu
Future<Map<String, dynamic>> getDeviceInfo() async {
  try {
    final DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
    final PackageInfo packageInfo = await PackageInfo.fromPlatform();

    String deviceId = '';
    String deviceModel = '';
    String osVersion = '';

    if (Platform.isAndroid) {
      final AndroidDeviceInfo androidInfo = await deviceInfo.androidInfo;
      deviceId = androidInfo.id; // Unikalny ID urządzenia
      deviceModel = '${androidInfo.manufacturer} ${androidInfo.model}';
      osVersion = 'Android ${androidInfo.version.release}';
    } else if (Platform.isIOS) {
      final IosDeviceInfo iosInfo = await deviceInfo.iosInfo;
      deviceId = iosInfo.identifierForVendor ?? 'unknown_ios';
      deviceModel = '${iosInfo.name} ${iosInfo.model}';
      osVersion = 'iOS ${iosInfo.systemVersion}';
    }

    return {
      'device_id': deviceId,
      'device_model': deviceModel,
      'os_version': osVersion,
      'app_version': '${packageInfo.version}+${packageInfo.buildNumber}',
    };
  } catch (e) {
    // Fallback jeśli nie można pobrać informacji
    return {
      'device_id': 'unknown_device_${DateTime.now().millisecondsSinceEpoch}',
      'device_model': 'Unknown Device',
      'os_version': 'Unknown OS',
      'app_version': '1.0.0+1',
    };
  }
}

// Funkcja do sprawdzenia i rejestracji urządzenia
Future<Map<String, dynamic>> checkAndRegisterDevice(
  String workerId,
  Map<String, dynamic> deviceInfo,
  String userAction, { // "approved", "rejected", lub "check"
  String? location,
}) async {
  try {
    final url = Uri.parse('$baseUrl/check_device');

    final requestBody = {
      'worker_id': workerId,
      'device_info': {
        'device_id': deviceInfo['device_id'],
        'device_model': deviceInfo['device_model'],
        'os_version': deviceInfo['os_version'],
        'app_version': deviceInfo['app_version'],
        'location': location,
      },
      'user_action': userAction,
    };

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode(requestBody),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      return {'error': 'Błąd rejestracji urządzenia: ${response.statusCode}'};
    }
  } catch (e) {
    return {'error': 'Błąd połączenia: $e'};
  }
}
