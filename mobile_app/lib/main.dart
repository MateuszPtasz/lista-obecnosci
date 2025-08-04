import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:lista_obecnosci_app/api.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:lista_obecnosci_app/statistics_pin.dart';
// import 'package:package_info_plus/package_info_plus.dart';  // temporarily disabled
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
      theme: ThemeData(primarySwatch: Colors.blue, useMaterial3: true),
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
  String? _configVersion;

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

    // Uruchom sprawdzanie statusu co minutę
    Timer.periodic(Duration(minutes: 1), (timer) {
      if (_isWorking) {
        _checkWorkerStatusFromServer();
      }
    });
    await _loadMobileConfig();
    await _loadSavedData();
    await _checkForUpdates();
  }

  _loadAppVersion() async {
    try {
      // Tymczasowa implementacja bez package_info_plus
      setState(() {
        _currentAppVersion = '1.0.0';
      });
    } catch (e) {
      debugPrint('Błąd pobierania wersji aplikacji: $e');
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
      debugPrint('Błąd sprawdzania aktualizacji: $e');
    }
  }

  _showUpdateDialog() {
    showDialog(
      context: context,
      barrierDismissible: !_updateRequired,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(
            _updateRequired
                ? '⚠️ Wymagana aktualizacja'
                : '🚀 Dostępna aktualizacja',
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _updateInfo['update_message'] ??
                    'Dostępna nowa wersja aplikacji',
              ),
              const SizedBox(height: 10),
              Text('Aktualna wersja: $_currentAppVersion'),
              Text(
                'Najnowsza wersja: ${_updateInfo['latest_version'] ?? 'Nieznana'}',
              ),
              if (_updateInfo['features'] != null) ...[
                const SizedBox(height: 10),
                const Text(
                  'Nowości:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                ...(_updateInfo['features'] as List).map(
                  (feature) =>
                      Text('• $feature', style: const TextStyle(fontSize: 12)),
                ),
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
    final url =
        _updateInfo['play_store_url'] ??
        'https://play.google.com/store/apps/details?id=com.example.lista_obecnosci';
    try {
      if (await canLaunchUrl(Uri.parse(url))) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Nie można otworzyć sklepu Play Store'),
            ),
          );
        }
      }
    } catch (e) {
      debugPrint('Błąd otwierania Play Store: $e');
    }
  }

  _loadMobileConfig() async {
    try {
      // Sprawdź wersję konfiguracji
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String? savedConfigVersion = prefs.getString('config_version');

      // Pobierz aktualną wersję konfiguracji z serwera
      final versionResult = await getVersionInfo();
      String? serverConfigVersion;

      if (versionResult['config_version'] != null) {
        serverConfigVersion = versionResult['config_version'];
      } else if (versionResult['error'] == null) {
        // Fallback - jeśli nie ma errora, ale nie ma config_version
        debugPrint('Brak config_version w odpowiedzi serwera: $versionResult');
      }

      // Sprawdź czy trzeba odświeżyć konfigurację
      bool needsRefresh = savedConfigVersion != serverConfigVersion;

      if (needsRefresh) {
        debugPrint(
          'Wykryto nową wersję konfiguracji: $serverConfigVersion (poprzednia: $savedConfigVersion)',
        );
      }

      final result = await getMobileConfig();
      if (result['config'] != null) {
        setState(() {
          _appConfig = result['config'] ?? {};
          _configLoaded = true;
          _configVersion = serverConfigVersion;
        });

        // Zapisz nową wersję konfiguracji
        if (serverConfigVersion != null) {
          await prefs.setString('config_version', serverConfigVersion);
        }

        debugPrint(
          'Konfiguracja załadowana (v$serverConfigVersion): $_appConfig',
        );
        debugPrint(
          'STATS CHECK: daily_stats=${_appConfig['daily_stats']}, monthly_stats=${_appConfig['monthly_stats']}',
        );

        if (needsRefresh && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Konfiguracja została odświeżona do wersji $serverConfigVersion',
              ),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 3),
            ),
          );
        }
      } else if (result['error'] != null) {
        debugPrint('Błąd ładowania konfiguracji: ${result['error']}');
        // Ustaw domyślną konfigurację
        setState(() {
          _appConfig = {
            'timer_enabled': true,
            'field_blocking': true,
            'daily_stats': true,
          };
          _configLoaded = true;
          _configVersion = 'Błąd serwera';
        });
      }
    } catch (e) {
      debugPrint('Błąd połączenia z serwerem konfiguracji: $e');
      // Ustaw domyślną konfigurację
      setState(() {
        _appConfig = {
          'timer_enabled': true,
          'field_blocking': true,
          'daily_stats': true,
        };
        _configLoaded = true;
        _configVersion = 'Błąd połączenia';
      });
    }
  }

  // Funkcja sprawdzająca status pracownika na serwerze
  Future<void> _checkWorkerStatusFromServer() async {
    if (_employeeIdController.text.isEmpty) {
      return;
    }

    try {
      final statusResult = await checkWorkerStatus(_employeeIdController.text);
      print('📱 Status pracownika z serwera: $statusResult');

      // Jeśli udało się sprawdzić status i jest różnica między lokalnym a serwerowym
      if (statusResult['success'] == true) {
        final bool isWorkingOnServer = statusResult['is_working'] ?? false;

        // Jeśli lokalnie pracujemy, ale na serwerze nie - status rozbieżny
        if (_isWorking && !isWorkingOnServer) {
          print(
            '❗ Wykryto rozbieżność statusu: lokalnie pracuje, na serwerze nie',
          );

          // Pokaż dialog informujący o sytuacji
          _showStatusDiscrepancyDialog(statusResult);
        }
        // Jeśli lokalnie nie pracujemy, ale na serwerze tak - również rozbieżność
        else if (!_isWorking && isWorkingOnServer) {
          print(
            '❗ Wykryto rozbieżność statusu: lokalnie nie pracuje, na serwerze tak',
          );

          // Możemy również obsłużyć ten przypadek, ale jest mniej krytyczny
          // bo użytkownik może po prostu zacząć pracę, a praca wciąż trwa
        }
      }
    } catch (e) {
      print('❌ Błąd podczas sprawdzania statusu: $e');
    }
  }

  // Dialog informujący o rozbieżności statusu
  void _showStatusDiscrepancyDialog(Map<String, dynamic> serverStatus) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: Text('Uwaga: Wykryto rozbieżność statusu'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Twoja praca została zakończona na serwerze (prawdopodobnie przez administratora), '
                'ale aplikacja nadal pokazuje, że pracujesz.',
              ),
              SizedBox(height: 10),
              Text('Co chcesz zrobić?'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Aktualizujemy lokalny stan zgodnie z serwerem
                setState(() {
                  _isWorking = false;
                  _stopTimer();
                });
                _saveData(_employeeIdController.text, false, null);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Status pracy został zaktualizowany'),
                    backgroundColor: Colors.green,
                  ),
                );
              },
              child: Text('Synchronizuj z serwerem'),
            ),
          ],
        );
      },
    );
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

      // Sprawdź status na serwerze, aby upewnić się, że jest zgodny z lokalnym
      _checkWorkerStatusFromServer();
    }
  }

  _saveData(String employeeId, bool isWorking, String? startTime) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('employee_id', employeeId);
    await prefs.setBool('is_working', isWorking);
    if (startTime != null) {
      await prefs.setString('last_start_time', startTime);
      if (_workStartDateTime != null) {
        await prefs.setString(
          'work_start_datetime',
          _workStartDateTime!.toIso8601String(),
        );
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
                color: _isWorking
                    ? Colors.green.shade100
                    : Colors.grey.shade100,
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
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
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
              keyboardType: TextInputType.text,
              decoration: InputDecoration(
                labelText: 'ID pracownika',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.person),
                filled: _isWorking && (_appConfig['field_blocking'] == true),
                fillColor: _isWorking && (_appConfig['field_blocking'] == true)
                    ? Colors.grey.shade200
                    : null,
                helperText: _isWorking && (_appConfig['field_blocking'] == true)
                    ? 'Pole zablokowane podczas pracy'
                    : null,
              ),
              enabled:
                  !_isLoading &&
                  !(_isWorking &&
                      (_appConfig['field_blocking'] ==
                          true)), // Zablokuj gdy pracownik jest w pracy i konfiguracja to pozwala
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
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.play_arrow),
                  label: Text(
                    _isLoading ? 'ROZPOCZYNAM...' : 'ROZPOCZNIJ PRACĘ',
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ] else ...[
              // Przyciski dodatkowe dla aktywnej pracy
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _isLoading
                          ? null
                          : () {
                              _checkWorkerStatusFromServer();
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Sprawdzanie statusu...'),
                                  duration: Duration(seconds: 2),
                                ),
                              );
                            },
                      icon: Icon(Icons.refresh, size: 20),
                      label: Text('ODŚWIEŻ STATUS'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  SizedBox(width: 8),
                ],
              ),
              SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _stopWork,
                  icon: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.stop),
                  label: Text(_isLoading ? 'KOŃCZĘ...' : 'ZAKOŃCZ PRACĘ'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],

            // Przycisk STATYSTYKI (widoczny tylko gdy włączony w konfiguracji)
            // DEBUG: Sprawdź dokładnie co jest w konfiguracji
            Builder(
              builder: (context) {
                debugPrint('=== BUTTON VISIBILITY CHECK ===');
                debugPrint(
                  'daily_stats value: ${_appConfig['daily_stats']} (type: ${_appConfig['daily_stats'].runtimeType})',
                );
                debugPrint(
                  'monthly_stats value: ${_appConfig['monthly_stats']} (type: ${_appConfig['monthly_stats'].runtimeType})',
                );
                debugPrint(
                  'Condition result: ${_appConfig['daily_stats'] == true || _appConfig['monthly_stats'] == true}',
                );
                debugPrint('Config loaded: $_configLoaded');
                debugPrint('Full config: $_appConfig');
                return const SizedBox.shrink();
              },
            ),
            if (_configLoaded &&
                (_appConfig['daily_stats'] == true ||
                    _appConfig['monthly_stats'] == true)) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton.icon(
                  onPressed: () {
                    final employeeId = _employeeIdController.text.trim();
                    if (employeeId.isEmpty) {
                      // Pokaż komunikat o potrzebie wprowadzenia ID
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Wprowadź najpierw ID pracownika'),
                          backgroundColor: Colors.orange,
                        ),
                      );
                      return;
                    }

                    StatisticsPinWidget.showPinDialog(context, employeeId, (
                      stats,
                    ) {
                      // Wyświetl statystyki
                      StatisticsPinWidget.showStatistics(
                        context,
                        stats,
                        employeeId,
                      );
                    });
                  },
                  icon: const Icon(Icons.bar_chart),
                  label: const Text('STATYSTYKI'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
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
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                        TextButton.icon(
                          onPressed: _checkForUpdates,
                          icon: const Icon(Icons.refresh, size: 16),
                          label: const Text(
                            'Sprawdź aktualizacje',
                            style: TextStyle(fontSize: 10),
                          ),
                          style: TextButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Wersja: $_currentAppVersion',
                      style: const TextStyle(fontSize: 11),
                    ),
                    Text(
                      'Konfiguracja: ${_configVersion ?? 'Nieznana'}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: Colors.blue,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    if (_updateAvailable)
                      Text(
                        '🚀 Dostępna aktualizacja: ${_updateInfo['latest_version'] ?? 'Nieznana'}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: Colors.green,
                        ),
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
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      height: 32,
                      child: ElevatedButton(
                        onPressed: () async {
                          debugPrint('RĘCZNE ODŚWIEŻANIE KONFIGURACJI');
                          await _loadMobileConfig();
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Konfiguracja odświeżona'),
                              backgroundColor: Colors.blue,
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                        ),
                        child: const Text(
                          'ODŚWIEŻ KONFIGURACJĘ',
                          style: TextStyle(fontSize: 10),
                        ),
                      ),
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

  // Sprawdza, czy jest rozbieżność między stanem aplikacji a stanem na serwerze
  Future<void> _checkAndSyncWorkStatus() async {
    if (_employeeIdController.text.isEmpty) {
      return;
    }

    try {
      final statusResult = await checkWorkerStatus(_employeeIdController.text);
      print('📱 Sprawdzanie i synchronizacja statusu pracy: $statusResult');

      if (statusResult['success'] == true) {
        final bool isWorkingOnServer = statusResult['is_working'] ?? false;

        if (_isWorking != isWorkingOnServer) {
          print('❗ Wykryto rozbieżność statusu - synchronizacja');

          // Jeśli status się różni, aktualizujemy lokalny stan
          setState(() {
            _isWorking = isWorkingOnServer;

            if (isWorkingOnServer) {
              // Pracownik pracuje na serwerze, ale lokalnie nie - aktualizujemy dane lokalne
              _lastStartTime = _formatTimeFromIso(statusResult['start_time']);
              _workStartDateTime = DateTime.parse(statusResult['start_time']);
              _startTimer();
            } else {
              // Pracownik nie pracuje na serwerze, ale lokalnie tak - zatrzymujemy timer
              _stopTimer();
            }
          });

          // Zapisujemy zaktualizowany stan
          _saveData(
            _employeeIdController.text,
            isWorkingOnServer,
            isWorkingOnServer ? _lastStartTime : null,
          );

          // Informujemy użytkownika
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                isWorkingOnServer
                    ? 'Stan pracy został zaktualizowany - jesteś w pracy'
                    : 'Stan pracy został zaktualizowany - nie pracujesz',
              ),
              backgroundColor: isWorkingOnServer ? Colors.green : Colors.blue,
            ),
          );
        } else {
          print('✅ Status pracy jest zgodny z serwerem');
        }
      }
    } catch (e) {
      print('❌ Błąd podczas synchronizacji statusu pracy: $e');
    }
  }

  // Pomocnicza funkcja do formatowania czasu z ISO
  String? _formatTimeFromIso(String? isoTime) {
    if (isoTime == null) return null;
    try {
      final dateTime = DateTime.parse(isoTime);
      return "${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}";
    } catch (e) {
      print('❌ Błąd formatowania czasu: $e');
      return null;
    }
  }

  _startWork() async {
    if (_employeeIdController.text.trim().isEmpty) {
      _showSnackbar("Wprowadź ID pracownika!");
      return;
    }

    // Najpierw sprawdzamy aktualny status na serwerze
    await _checkAndSyncWorkStatus();

    // Jeśli po synchronizacji pracownik jest już w pracy, nie rozpoczynamy pracy ponownie
    if (_isWorking) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Jesteś już w pracy!'),
          backgroundColor: Colors.orange,
        ),
      );
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
          content: const Text(
            'Musisz wyrazić zgodę na lokalizację, aby rozpocząć pracę.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
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
          _lastStartTime =
              '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
          _workStartDateTime = now;
        });
        await _saveData(
          _employeeIdController.text.trim(),
          true,
          _lastStartTime,
        );
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
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }
}
