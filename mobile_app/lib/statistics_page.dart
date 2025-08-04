import 'package:flutter/material.dart';
import 'package:lista_obecnosci_app/api.dart' as api;

class StatisticsPage extends StatefulWidget {
  final String workerId;

  const StatisticsPage({super.key, required this.workerId});

  @override
  State<StatisticsPage> createState() => _StatisticsPageState();
}

class _StatisticsPageState extends State<StatisticsPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  Map<String, dynamic> _statsData = {};
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadStatistics();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadStatistics() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await api.getWorkerStats(widget.workerId);

      if (result['success'] == true) {
        setState(() {
          _statsData = result['data'] ?? {};
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = result['error'] ?? 'Błąd pobierania statystyk';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Błąd połączenia: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Statystyki - ID: ${widget.workerId}'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Podsumowanie'),
            Tab(icon: Icon(Icons.calendar_today), text: 'Dzienne'),
            Tab(icon: Icon(Icons.date_range), text: 'Tygodniowe'),
            Tab(icon: Icon(Icons.calendar_month), text: 'Miesięczne'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadStatistics,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
          ? _buildErrorWidget()
          : TabBarView(
              controller: _tabController,
              children: [
                _buildSummaryTab(),
                _buildDailyTab(),
                _buildWeeklyTab(),
                _buildMonthlyTab(),
              ],
            ),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
          const SizedBox(height: 16),
          Text(
            'Błąd ładowania statystyk',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            _errorMessage ?? 'Nieznany błąd',
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadStatistics,
            icon: const Icon(Icons.refresh),
            label: const Text('Spróbuj ponownie'),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryTab() {
    if (_statsData.isEmpty) return const Center(child: Text('Brak danych'));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Karty z głównymi statystykami
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  'Łącznie godzin',
                  '${_statsData['total_hours']?.toStringAsFixed(1) ?? '0'} h',
                  Icons.access_time,
                  Colors.blue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  'Dni pracy',
                  '${_statsData['total_days'] ?? 0}',
                  Icons.calendar_today,
                  Colors.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  'Ten tydzień',
                  '${_statsData['this_week_hours']?.toStringAsFixed(1) ?? '0'} h',
                  Icons.date_range,
                  Colors.orange,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  'Ten miesiąc',
                  '${_statsData['this_month_hours']?.toStringAsFixed(1) ?? '0'} h',
                  Icons.calendar_month,
                  Colors.purple,
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Średnie
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Średnie wartości',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildAverageRow(
                    'Godzin na dzień',
                    '${_statsData['summary']?['average_hours_per_day']?.toStringAsFixed(1) ?? '0'} h',
                  ),
                  _buildAverageRow(
                    'Godzin w tym tygodniu',
                    '${_statsData['summary']?['average_hours_per_week']?.toStringAsFixed(1) ?? '0'} h',
                  ),
                  _buildAverageRow(
                    'Godzin w tym miesiącu',
                    '${_statsData['summary']?['average_hours_per_month']?.toStringAsFixed(1) ?? '0'} h',
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Ostatnie zmiany
          Text(
            'Ostatnie zmiany',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          ..._buildRecentShifts(),
        ],
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAverageRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  List<Widget> _buildRecentShifts() {
    final recentShifts = _statsData['recent_shifts'] as List? ?? [];

    if (recentShifts.isEmpty) {
      return [
        const Card(
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Text('Brak danych o zmianach'),
          ),
        ),
      ];
    }

    return recentShifts.map((shift) {
      return Card(
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: Colors.blue.shade100,
            child: Text(
              shift['date'].toString().substring(8, 10), // dzień
              style: TextStyle(
                color: Colors.blue.shade700,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          title: Text(shift['date']),
          subtitle: Text('${shift['start_time']} - ${shift['stop_time']}'),
          trailing: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${shift['hours']} h',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              Text(
                shift['duration_text'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      );
    }).toList();
  }

  Widget _buildDailyTab() {
    final dailyStats = _statsData['daily_stats'] as List? ?? [];

    if (dailyStats.isEmpty) {
      return const Center(child: Text('Brak danych dziennych'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: dailyStats.length,
      itemBuilder: (context, index) {
        final day = dailyStats[index];
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.green.shade100,
              child: Text(
                day['date'].toString().substring(8, 10),
                style: TextStyle(
                  color: Colors.green.shade700,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            title: Text(_formatDate(day['date'])),
            subtitle: Text('${day['shifts']} zmian(y)'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${day['hours'].toStringAsFixed(1)} h',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  _formatDuration(day['hours']),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildWeeklyTab() {
    final weeklyStats = _statsData['weekly_stats'] as List? ?? [];

    if (weeklyStats.isEmpty) {
      return const Center(child: Text('Brak danych tygodniowych'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: weeklyStats.length,
      itemBuilder: (context, index) {
        final week = weeklyStats[index];
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.orange.shade100,
              child: Icon(Icons.date_range, color: Colors.orange.shade700),
            ),
            title: Text('Tydzień od ${_formatDate(week['week_start'])}'),
            subtitle: Text('${week['days']} dni pracy'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${week['hours'].toStringAsFixed(1)} h',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  _formatDuration(week['hours']),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildMonthlyTab() {
    final monthlyStats = _statsData['monthly_summary'] as List? ?? [];

    if (monthlyStats.isEmpty) {
      return const Center(child: Text('Brak danych miesięcznych'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: monthlyStats.length,
      itemBuilder: (context, index) {
        final month = monthlyStats[index];
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.purple.shade100,
              child: Icon(Icons.calendar_month, color: Colors.purple.shade700),
            ),
            title: Text('${month['month_name']} ${month['year']}'),
            subtitle: Text('${month['days']} dni pracy'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${month['hours'].toStringAsFixed(1)} h',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  _formatDuration(month['hours']),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final months = [
        'stycznia',
        'lutego',
        'marca',
        'kwietnia',
        'maja',
        'czerwca',
        'lipca',
        'sierpnia',
        'września',
        'października',
        'listopada',
        'grudnia',
      ];
      return '${date.day} ${months[date.month - 1]} ${date.year}';
    } catch (e) {
      return dateStr;
    }
  }

  String _formatDuration(double hours) {
    final h = hours.floor();
    final m = ((hours - h) * 60).round();
    return '${h}h ${m}min';
  }
}
