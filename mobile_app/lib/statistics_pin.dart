import 'package:flutter/material.dart';
import 'package:lista_obecnosci_app/api.dart' as api;

class StatisticsPinWidget {
  // Przechowujemy PIN po udanej weryfikacji dla sesji
  static String? _verifiedPin;
  static String? _verifiedWorkerId;
  static DateTime? _pinVerificationTime;

  // Funkcja czyszcząca sesję
  static void _clearSession() {
    _verifiedPin = null;
    _verifiedWorkerId = null;
    _pinVerificationTime = null;
  }

  static void showPinDialog(
    BuildContext context,
    String workerId,
    Function(Map<String, dynamic>) onSuccess,
  ) {
    final TextEditingController pinController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('🔐 Dostęp do statystyk'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Wprowadź PIN dla pracownika: $workerId',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: pinController,
                obscureText: true,
                keyboardType: TextInputType.text,
                maxLength: 4,
                decoration: const InputDecoration(
                  labelText: 'PIN (4 znaki)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Anuluj'),
            ),
            ElevatedButton(
              onPressed: () async {
                final pin = pinController.text;
                Navigator.of(context).pop(); // Zamknij dialog PIN PIERWSZY
                await _verifyPin(context, workerId, pin, onSuccess);
              },
              child: const Text('Potwierdź'),
            ),
          ],
        );
      },
    );
  }

  static Future<void> _verifyPin(
    BuildContext context,
    String workerId,
    String pin,
    Function(Map<String, dynamic>) onSuccess,
  ) async {
    if (pin.isEmpty) {
      _showSnackbar(context, 'Wprowadź PIN');
      return;
    }

    // Pokazuje loading DOPIERO po zamknięciu dialogu PIN
    if (!context.mounted) return;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext loadingContext) {
        return const AlertDialog(
          content: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 20),
              Text('Weryfikacja PIN...'),
            ],
          ),
        );
      },
    );

    try {
      // Domyślnie użyj miesiąca
      final result = await api.verifyPinForStatistics(
        workerId,
        pin,
        periodType: 'month',
      );

      // Sprawdź czy context jest nadal aktywny przed zamknięciem loading
      if (context.mounted) {
        Navigator.of(context).pop(); // Zamknij loading
      }

      print('PIN verification result: ${result.toString()}');

      if (result['success'] == true) {
        // Zapisz PIN i dane weryfikacji dla sesji
        _verifiedPin = pin;
        _verifiedWorkerId = workerId;
        _pinVerificationTime = DateTime.now();

        if (result['device_changed'] == true && context.mounted) {
          _showDeviceChangeAlert(context);
        }

        // Sprawdź czy statystyki są w odpowiedzi na weryfikację PIN
        if (result['statistics'] != null) {
          print('Statistics data: ${result['statistics'].toString()}');
          if (context.mounted) {
            // Pokaż statystyki z możliwością zmiany okresu
            showStatistics(context, result['statistics'], workerId);
          }
        } else {
          print('No statistics in response, trying separate call...');
          // Fallback - pobierz statystyki osobno
          final statsResult = await api.getWorkerStatisticsByPeriod(
            workerId,
            periodType: 'month',
          );
          if (statsResult['success'] == true && context.mounted) {
            showStatistics(context, statsResult['data'], workerId);
          } else {
            if (context.mounted) {
              _showSnackbar(
                context,
                statsResult['message'] ?? 'Błąd pobierania statystyk',
              );
            }
          }
        }
      } else {
        if (context.mounted) {
          _showSnackbar(
            context,
            result['message'] ??
                'Niepoprawny PIN. Próba została zarejestrowana.',
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.of(context).pop(); // Zamknij loading
        _showSnackbar(context, 'Błąd weryfikacji PIN: $e');
      }
    }
  }

  static void _showDeviceChangeAlert(BuildContext context) {
    if (!context.mounted) return;
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('⚠️ Zmiana urządzenia'),
          content: const Text(
            'Wykryto logowanie z nowego urządzenia. Administrator został powiadomiony o tej sytuacji.',
          ),
          actions: [
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Rozumiem'),
            ),
          ],
        );
      },
    );
  }

  static void _showSnackbar(BuildContext context, String message) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  static void showStatistics(
    BuildContext context,
    Map<String, dynamic> data,
    String workerId,
  ) {
    print('Showing statistics with data: ${data.toString()}');

    if (!context.mounted) return;

    // Sprawdź czy mamy wymagane dane
    if (data.isEmpty) {
      _showSnackbar(context, 'Brak danych statystyk');
      return;
    }

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('📊 Statystyki - ${data['worker_id'] ?? 'Nieznany'}'),
          content: SizedBox(
            width: double.maxFinite,
            height: 500,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Informacja o okresie i przycisk zmiany
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.date_range, color: Colors.green),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${data['period_name'] ?? 'Ostatnie 30 dni'}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(
                            Icons.edit_calendar,
                            color: Colors.green,
                          ),
                          onPressed: () {
                            Navigator.of(context).pop();
                            _showPeriodSelector(context, workerId);
                          },
                          tooltip: 'Zmień okres',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Podsumowanie
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '📈 Podsumowanie',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 8),
                        _buildStatRow(
                          'Łączne godziny:',
                          '${data['total_hours'] ?? 0} h',
                        ),
                        _buildStatRow(
                          'Dni pracy:',
                          '${data['total_days'] ?? 0}',
                        ),
                        if (data['total_shifts'] != null)
                          _buildStatRow(
                            'Liczba zmian:',
                            '${data['total_shifts']}',
                          ),
                        _buildStatRow(
                          'Średnio/dzień:',
                          '${data['average_hours_per_day'] ?? 0} h',
                        ),

                        // Ostrzeżenie o podejrzanych danych
                        if (data['total_hours'] != null &&
                            data['total_hours'] > 1000) ...[
                          const SizedBox(height: 8),
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.orange.shade100,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Row(
                              children: [
                                Icon(
                                  Icons.warning,
                                  color: Colors.orange,
                                  size: 16,
                                ),
                                SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    'Wykryto podejrzane dane - skontaktuj się z administratorem',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.orange,
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

                  const SizedBox(height: 16),

                  // Ostatnie zmiany
                  const Text(
                    '🕒 Ostatnie zmiany',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 8),

                  if (data['recent_shifts'] != null &&
                      data['recent_shifts'].isNotEmpty) ...[
                    for (var shift in data['recent_shifts'])
                      Container(
                        margin: const EdgeInsets.only(bottom: 4),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.grey.shade100,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('${shift['date'] ?? 'N/A'}'),
                            Text(
                              '${shift['start'] ?? 'N/A'} - ${shift['stop'] ?? 'N/A'}',
                            ),
                            Text(
                              '${shift['hours'] ?? 0} h',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ] else ...[
                    const Text('Brak danych o zmianach w wybranym okresie'),
                  ],

                  // Pokaż błąd jeśli wystąpił
                  if (data['error'] != null) ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '⚠️ Błąd',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.red,
                            ),
                          ),
                          Text('${data['error']}'),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                _clearSession(); // Wyczyść sesję PIN przy zamknięciu
                Navigator.of(context).pop();
              },
              child: const Text('Zamknij'),
            ),
          ],
        );
      },
    );
  }

  static void _showPeriodSelector(BuildContext context, String workerId) {
    if (!context.mounted) return;

    String selectedPeriod = 'month';
    DateTime? customStartDate;
    DateTime? customEndDate;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('📅 Wybierz okres statystyk'),
              content: SizedBox(
                width: double.maxFinite,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Przyciski wyboru okresu
                    Wrap(
                      spacing: 8,
                      children: [
                        _buildPeriodChip('day', 'Dzisiaj', selectedPeriod, (
                          value,
                        ) {
                          setState(() => selectedPeriod = value);
                        }),
                        _buildPeriodChip('week', '7 dni', selectedPeriod, (
                          value,
                        ) {
                          setState(() => selectedPeriod = value);
                        }),
                        _buildPeriodChip('month', '30 dni', selectedPeriod, (
                          value,
                        ) {
                          setState(() => selectedPeriod = value);
                        }),
                        _buildPeriodChip('custom', 'Okres', selectedPeriod, (
                          value,
                        ) {
                          setState(() => selectedPeriod = value);
                        }),
                      ],
                    ),

                    // Wybór dat dla custom
                    if (selectedPeriod == 'custom') ...[
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: GestureDetector(
                              onTap: () async {
                                final date = await showDatePicker(
                                  context: context,
                                  initialDate:
                                      customStartDate ??
                                      DateTime.now().subtract(
                                        Duration(days: 30),
                                      ),
                                  firstDate: DateTime(2020),
                                  lastDate: DateTime.now(),
                                );
                                if (date != null) {
                                  setState(() => customStartDate = date);
                                }
                              },
                              child: Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.grey),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  customStartDate?.toString().split(' ')[0] ??
                                      'Od...',
                                  style: TextStyle(
                                    color: customStartDate != null
                                        ? Colors.black
                                        : Colors.grey,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: GestureDetector(
                              onTap: () async {
                                final date = await showDatePicker(
                                  context: context,
                                  initialDate: customEndDate ?? DateTime.now(),
                                  firstDate: customStartDate ?? DateTime(2020),
                                  lastDate: DateTime.now(),
                                );
                                if (date != null) {
                                  setState(() => customEndDate = date);
                                }
                              },
                              child: Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.grey),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  customEndDate?.toString().split(' ')[0] ??
                                      'Do...',
                                  style: TextStyle(
                                    color: customEndDate != null
                                        ? Colors.black
                                        : Colors.grey,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Anuluj'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    // Sprawdź poprawność danych dla custom period
                    if (selectedPeriod == 'custom') {
                      if (customStartDate == null || customEndDate == null) {
                        _showSnackbar(
                          context,
                          'Wybierz daty początkową i końcową',
                        );
                        return;
                      }
                      if (customStartDate!.isAfter(customEndDate!)) {
                        _showSnackbar(
                          context,
                          'Data początkowa nie może być późniejsza niż końcowa',
                        );
                        return;
                      }
                    }

                    Navigator.of(context).pop();
                    await _loadStatisticsForPeriod(
                      context,
                      workerId,
                      selectedPeriod,
                      customStartDate,
                      customEndDate,
                    );
                  },
                  child: const Text('Pokaż statystyki'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  static Future<void> _loadStatisticsForPeriod(
    BuildContext context,
    String workerId,
    String periodType,
    DateTime? startDate,
    DateTime? endDate,
  ) async {
    if (!context.mounted) return;

    // Sprawdź czy mamy zapisany PIN dla tego pracownika
    if (_verifiedPin == null ||
        _verifiedWorkerId != workerId ||
        _pinVerificationTime == null) {
      if (context.mounted) {
        _showSnackbar(context, 'Błąd sesji. Wprowadź PIN ponownie.');
      }
      return;
    }

    // Sprawdź czy PIN nie wygasł (30 minut)
    if (DateTime.now().difference(_pinVerificationTime!).inMinutes > 30) {
      if (context.mounted) {
        _showSnackbar(context, 'Sesja wygasła. Wprowadź PIN ponownie.');
      }
      return;
    }

    // Pokazuje loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return const AlertDialog(
          content: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 20),
              Text('Ładowanie statystyk...'),
            ],
          ),
        );
      },
    );

    try {
      String? startDateStr;
      String? endDateStr;

      if (periodType == 'custom' && startDate != null && endDate != null) {
        startDateStr =
            '${startDate.year}-${startDate.month.toString().padLeft(2, '0')}-${startDate.day.toString().padLeft(2, '0')}';
        endDateStr =
            '${endDate.year}-${endDate.month.toString().padLeft(2, '0')}-${endDate.day.toString().padLeft(2, '0')}';
      }

      // Użyj verifyPinForStatistics z zapisanym PIN-em i nowym okresem
      final result = await api.verifyPinForStatistics(
        workerId,
        _verifiedPin!,
        periodType: periodType,
        startDate: startDateStr,
        endDate: endDateStr,
      );

      // Zamknij loading
      if (context.mounted) {
        Navigator.of(context).pop();
      }

      if (result['success'] == true && context.mounted) {
        // Odśwież czas weryfikacji
        _pinVerificationTime = DateTime.now();

        // Sprawdź czy mamy statystyki w result
        if (result['statistics'] != null) {
          showStatistics(context, result['statistics'], workerId);
        } else {
          _showSnackbar(context, 'Brak danych statystyk');
        }
      } else {
        if (context.mounted) {
          _showSnackbar(
            context,
            result['message'] ?? 'Błąd pobierania statystyk',
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.of(context).pop(); // Zamknij loading
        _showSnackbar(context, 'Błąd ładowania statystyk: $e');
      }
    }
  }

  static Widget _buildPeriodChip(
    String value,
    String label,
    String selectedValue,
    Function(String) onTap,
  ) {
    final isSelected = value == selectedValue;
    return GestureDetector(
      onTap: () => onTap(value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue : Colors.white,
          border: Border.all(color: Colors.blue),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.blue,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  static Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value, style: const TextStyle(fontSize: 16)),
        ],
      ),
    );
  }
}
