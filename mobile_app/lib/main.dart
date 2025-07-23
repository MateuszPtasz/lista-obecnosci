import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:lista_obecnosci_app/api.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'dart:async';

Future<bool> checkLocationPermission() async {
  LocationPermission permission = await Geolocator.checkPermission();

  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
  }

  if (permission == LocationPermission.deniedForever ||
      permission == LocationPermission.denied) {
    return false;
  }

  return true;
}

Future<Position> getCurrentLocation() async {
  bool serviceEnabled;
  LocationPermission permission;

  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    throw Exception('Lokalizacja jest wyłączona.');
  }

  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      throw Exception('Brak pozwolenia na lokalizację.');
    }
  }

  if (permission == LocationPermission.deniedForever) {
    throw Exception('Lokalizacja zablokowana.');
  }

  return await Geolocator.getCurrentPosition();
}

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lista Obecności',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const AttendancePage(),
    );
  }
}

class AttendancePage extends StatefulWidget {
  const AttendancePage({super.key});

  @override
  State<AttendancePage> createState() => _AttendancePageState();
}

class _AttendancePageState extends State<AttendancePage> {
  final TextEditingController _employeeIdController = TextEditingController();
  bool _isWorking = false;
  bool _isLoading = false;
  String? _lastStartTime;
  DateTime? _workStartDateTime;
  String _elapsedTime = "00:00:00";
  Timer? _timer;
  
  // Konfiguracja z serwera
  Map<String, dynamic> _appConfig = {};
  bool _configLoaded = false;
  
  // Informacje o aktualizacjach
  String _currentAppVersion = "1.0.0";
  bool _updateAvailable = false;
  bool _updateRequired = false;
  Map<String, dynamic> _updateInfo = {};

  @override
  void initState() {
    super.initState();
    _loadConfigAndData();
  }

  _loadConfigAndData() async {
    await _loadAppVersion();
    await _loadMobileConfig();
    await _loadSavedData();
    await _checkForUpdates();
  }

  _loadAppVersion() async {
    try {
      PackageInfo packageInfo = await PackageInfo.fromPlatform();
      setState(() {
        _currentAppVersion = packageInfo.version;
      });
    } catch (e) {
      print('Błąd pobierania wersji aplikacji: $e');
    }
  }

  _checkForUpdates() async {
    // Sprawdź aktualizacje tylko jeśli auto-updates jest włączone
    if (_appConfig['auto_updates'] != true) return;
    
    try {
      final result = await checkForUpdates(_currentAppVersion);
      if (result['success'] && result['data'] != null) {
        final data = result['data'];
        setState(() {
          _updateAvailable = data['update_available'] ?? false;
          _updateRequired = data['update_required'] ?? false;
          _updateInfo = data;
        });
        
        // Pokaż dialog o aktualizacji
        if (_updateAvailable && mounted) {
          _showUpdateDialog();
        }
      }
    } catch (e) {
      print('Błąd sprawdzania aktualizacji: $e');
    }
  }

  _showUpdateDialog() {
    showDialog(
      context: context,
      barrierDismissible: !_updateRequired,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(_updateRequired ? '⚠️ Wymagana aktualizacja' : '🚀 Dostępna aktualizacja'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_updateInfo['update_message'] ?? 'Dostępna nowa wersja aplikacji'),
              const SizedBox(height: 10),
              Text('Aktualna wersja: $_currentAppVersion'),
              Text('Najnowsza wersja: ${_updateInfo['latest_version'] ?? 'Nieznana'}'),
              if (_updateInfo['features'] != null) ...[
                const SizedBox(height: 10),
                const Text('Nowości:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...(_updateInfo['features'] as List).map((feature) => 
                  Text('• $feature', style: const TextStyle(fontSize: 12))),
              ],
            ],
          ),
          actions: [
            if (!_updateRequired)
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Później'),
              ),
            ElevatedButton(
              onPressed: () async {
                Navigator.of(context).pop();
                await _openPlayStore();
              },
              child: Text(_updateRequired ? 'Aktualizuj teraz' : 'Pobierz'),
            ),
          ],
        );
      },
    );
  }

  _openPlayStore() async {
    final url = _updateInfo['play_store_url'] ?? 'https://play.google.com/store/apps/details?id=com.example.lista_obecnosci';
    try {
      if (await canLaunchUrl(Uri.parse(url))) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Nie można otworzyć sklepu Play Store')),
          );
        }
      }
    } catch (e) {
      print('Błąd otwierania Play Store: $e');
    }
  }

  _loadMobileConfig() async {
    try {
      // Sprawdź wersję konfiguracji
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String? savedConfigVersion = prefs.getString('config_version');
      
      // Pobierz aktualną wersję konfiguracji z serwera
      final versionResult = await getConfigVersion();
      String? serverConfigVersion;
      
      if (versionResult['success']) {
        serverConfigVersion = versionResult['data']['version'];
      }
      
      // Sprawdź czy trzeba odświeżyć konfigurację
      bool needsRefresh = savedConfigVersion != serverConfigVersion;
      
      if (needsRefresh) {
        print('Wykryto nową wersję konfiguracji: $serverConfigVersion (poprzednia: $savedConfigVersion)');
      }
      
      final result = await getMobileConfig();
      if (result['success']) {
        setState(() {
          _appConfig = result['config']['config'] ?? {};
          _configLoaded = true;
        });
        
        // Zapisz nową wersję konfiguracji
        if (serverConfigVersion != null) {
          await prefs.setString('config_version', serverConfigVersion);
        }
        
        print('Konfiguracja załadowana (v$serverConfigVersion): $_appConfig');
        
        if (needsRefresh && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Konfiguracja została odświeżona'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 3),
            ),
          );
        }
      } else {
        print('Błąd ładowania konfiguracji: ${result['message']}');
        // Ustaw domyślną konfigurację
        setState(() {
          _appConfig = {
            'timer_enabled': true,
            'field_blocking': true,
            'daily_stats': true,
          };
          _configLoaded = true;
        });
      }
    } catch (e) {
      print('Błąd połączenia z serwerem konfiguracji: $e');
      // Ustaw domyślną konfigurację
      setState(() {
        _appConfig = {
          'timer_enabled': true,
          'field_blocking': true,
          'daily_stats': true,
        };
        _configLoaded = true;
      });
    }
  }

  _loadSavedData() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _employeeIdController.text = prefs.getString('employee_id') ?? '';
      _isWorking = prefs.getBool('is_working') ?? false;
      _lastStartTime = prefs.getString('last_start_time');
    });
    
    // Jeśli pracownik jest w pracy, ustaw czas rozpoczęcia i uruchom timer
    if (_isWorking && _lastStartTime != null) {
      final savedStartDateTime = prefs.getString('work_start_datetime');
      if (savedStartDateTime != null) {
        _workStartDateTime = DateTime.parse(savedStartDateTime);
        _startTimer();
      }
    }
  }

  _saveData(String employeeId, bool isWorking, String? startTime) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('employee_id', employeeId);
    await prefs.setBool('is_working', isWorking);
    if (startTime != null) {
      await prefs.setString('last_start_time', startTime);
      if (_workStartDateTime != null) {
        await prefs.setString('work_start_datetime', _workStartDateTime!.toIso8601String());
      }
    } else {
      await prefs.remove('last_start_time');
      await prefs.remove('work_start_datetime');
    }
  }

  void _startTimer() {
    // Sprawdź czy timer jest włączony w konfiguracji
    if (_appConfig['timer_enabled'] == true) {
      _timer?.cancel();
      _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
        if (_workStartDateTime != null) {
          final now = DateTime.now();
          final elapsed = now.difference(_workStartDateTime!);
          setState(() {
            _elapsedTime = _formatDuration(elapsed);
          });
        }
      });
    }
  }

  void _stopTimer() {
    _timer?.cancel();
    setState(() {
      _elapsedTime = "00:00:00";
    });
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours.toString().padLeft(2, '0');
    final minutes = (duration.inMinutes % 60).toString().padLeft(2, '0');
    final seconds = (duration.inSeconds % 60).toString().padLeft(2, '0');
    return "$hours:$minutes:$seconds";
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Lista Obecności'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            // Status pracownika
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _isWorking ? Colors.green.shade100 : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _isWorking ? Colors.green : Colors.grey,
                  width: 2,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    _isWorking ? Icons.work : Icons.work_off,
                    size: 48,
                    color: _isWorking ? Colors.green : Colors.grey,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _isWorking ? 'W PRACY' : 'NIE W PRACY',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: _isWorking ? Colors.green : Colors.grey,
                    ),
                  ),
                  if (_isWorking && _lastStartTime != null) ...[
                    Text(
                      'Od: $_lastStartTime',
                      style: TextStyle(color: Colors.grey.shade600),
                    ),
                    if (_appConfig['timer_enabled'] == true) ...[
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.green.shade50,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.green.shade300),
                        ),
                        child: Text(
                          _elapsedTime,
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.green.shade700,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                    ],
                  ],
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Pole ID pracownika
            TextField(
              controller: _employeeIdController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'Numer pracownika',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.person),
                filled: _isWorking && (_appConfig['field_blocking'] == true),
                fillColor: _isWorking && (_appConfig['field_blocking'] == true) ? Colors.grey.shade200 : null,
                helperText: _isWorking && (_appConfig['field_blocking'] == true) ? 'Pole zablokowane podczas pracy' : null,
              ),
              enabled: !_isLoading && !(_isWorking && (_appConfig['field_blocking'] == true)), // Zablokuj gdy pracownik jest w pracy i konfiguracja to pozwala
            ),
            const SizedBox(height: 24),
            
            // Przyciski START/STOP
            if (!_isWorking) ...[
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _startWork,
                  icon: _isLoading 
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.play_arrow),
                  label: Text(_isLoading ? 'ROZPOCZYNAM...' : 'ROZPOCZNIJ PRACĘ'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ] else ...[
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _stopWork,
                  icon: _isLoading 
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.stop),
                  label: Text(_isLoading ? 'KOŃCZĘ...' : 'ZAKOŃCZ PRACĘ'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
            
            // Informacje o konfiguracji (tylko w trybie debug)
            if (_configLoaded) ...[
              const SizedBox(height: 32),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Konfiguracja:',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                        TextButton.icon(
                          onPressed: _checkForUpdates,
                          icon: const Icon(Icons.refresh, size: 16),
                          label: const Text('Sprawdź aktualizacje', style: TextStyle(fontSize: 10)),
                          style: TextButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Wersja: $_currentAppVersion',
                      style: const TextStyle(fontSize: 11),
                    ),
                    if (_updateAvailable)
                      Text(
                        '🚀 Dostępna aktualizacja: ${_updateInfo['latest_version'] ?? 'Nieznana'}',
                        style: const TextStyle(fontSize: 11, color: Colors.green),
                      ),
                    Text(
                      'Timer: ${_appConfig['timer_enabled'] == true ? 'ON' : 'OFF'}',
                      style: const TextStyle(fontSize: 11),
                    ),
                    Text(
                      'Blokada pól: ${_appConfig['field_blocking'] == true ? 'ON' : 'OFF'}',
                      style: const TextStyle(fontSize: 11),
                    ),
                    Text(
                      'Statystyki: ${_appConfig['daily_stats'] == true ? 'ON' : 'OFF'}',
                      style: const TextStyle(fontSize: 11),
                    ),
                    Text(
                      'Auto-aktualizacje: ${_appConfig['auto_updates'] == true ? 'ON' : 'OFF'}',
                      style: const TextStyle(fontSize: 11),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  _startWork() async {
    if (_employeeIdController.text.trim().isEmpty) {
      _showSnackbar("Wprowadź numer pracownika!");
      return;
    }

    setState(() => _isLoading = true);

    bool permissionGranted = await checkLocationPermission();
    if (!permissionGranted) {
      setState(() => _isLoading = false);
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Brak zgody na lokalizację'),
          content: const Text('Musisz wyrazić zgodę na lokalizację, aby rozpocząć pracę.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            )
          ],
        ),
      );
      return;
    }

    try {
      final pos = await getCurrentLocation();
      final now = DateTime.now();
      final result = await sendStart(
        _employeeIdController.text.trim(),
        pos.latitude,
        pos.longitude,
        now,
      );

      if (result['success']) {
        setState(() {
          _isWorking = true;
          _lastStartTime = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
          _workStartDateTime = now;
        });
        await _saveData(_employeeIdController.text.trim(), true, _lastStartTime);
        _startTimer(); // Rozpocznij licznik
        if (mounted) _showSnackbar(result['message']);
      } else {
        if (mounted) _showSnackbar(result['message']);
      }
    } catch (e) {
      if (mounted) _showSnackbar("Błąd: $e");
    }

    setState(() => _isLoading = false);
  }

  _stopWork() async {
    setState(() => _isLoading = true);

    try {
      final pos = await getCurrentLocation();
      final now = DateTime.now();
      final result = await sendStop(
        _employeeIdController.text.trim(),
        pos.latitude,
        pos.longitude,
        now,
      );

      if (result['success']) {
        setState(() {
          _isWorking = false;
          _lastStartTime = null;
          _workStartDateTime = null;
        });
        _stopTimer(); // Zatrzymaj licznik
        await _saveData(_employeeIdController.text.trim(), false, null);
        if (mounted) _showSnackbar(result['message']);
      } else {
        if (mounted) _showSnackbar(result['message']);
      }
    } catch (e) {
      if (mounted) _showSnackbar("Błąd: $e");
    }

    setState(() => _isLoading = false);
  }

  void _showSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
