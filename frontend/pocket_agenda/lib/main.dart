import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

void main() {
  runApp(const PocketAgendaApp());
}

class PocketAgendaApp extends StatelessWidget {
  const PocketAgendaApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF0E7C86);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Pocket Agenda',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: seed,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF6F7F4),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: const BorderSide(color: Color(0xFFE0E5DF)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Color(0xFFD7DDD6)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Color(0xFFD7DDD6)),
          ),
        ),
      ),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int selectedIndex = 0;

  final pages = const [SmartAddPage(), ChatPage(), PlannerPage(), AgendaPage()];

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width >= 840;

    return Scaffold(
      body: SafeArea(
        child: Row(
          children: [
            if (wide)
              NavigationRail(
                selectedIndex: selectedIndex,
                onDestinationSelected: (value) {
                  setState(() => selectedIndex = value);
                },
                labelType: NavigationRailLabelType.all,
                leading: const Padding(
                  padding: EdgeInsets.only(top: 16, bottom: 24),
                  child: AppMark(),
                ),
                destinations: const [
                  NavigationRailDestination(
                    icon: Icon(Icons.auto_awesome_outlined),
                    selectedIcon: Icon(Icons.auto_awesome),
                    label: Text('Smart Add'),
                  ),
                  NavigationRailDestination(
                    icon: Icon(Icons.chat_bubble_outline),
                    selectedIcon: Icon(Icons.chat_bubble),
                    label: Text('Chat'),
                  ),
                  NavigationRailDestination(
                    icon: Icon(Icons.calendar_month_outlined),
                    selectedIcon: Icon(Icons.calendar_month),
                    label: Text('Planner'),
                  ),
                  NavigationRailDestination(
                    icon: Icon(Icons.event_note_outlined),
                    selectedIcon: Icon(Icons.event_note),
                    label: Text('Agenda'),
                  ),
                ],
              ),
            Expanded(child: pages[selectedIndex]),
          ],
        ),
      ),
      bottomNavigationBar: wide
          ? null
          : NavigationBar(
              selectedIndex: selectedIndex,
              onDestinationSelected: (value) {
                setState(() => selectedIndex = value);
              },
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.auto_awesome_outlined),
                  selectedIcon: Icon(Icons.auto_awesome),
                  label: 'Add',
                ),
                NavigationDestination(
                  icon: Icon(Icons.chat_bubble_outline),
                  selectedIcon: Icon(Icons.chat_bubble),
                  label: 'Chat',
                ),
                NavigationDestination(
                  icon: Icon(Icons.calendar_month_outlined),
                  selectedIcon: Icon(Icons.calendar_month),
                  label: 'Plan',
                ),
                NavigationDestination(
                  icon: Icon(Icons.event_note_outlined),
                  selectedIcon: Icon(Icons.event_note),
                  label: 'Agenda',
                ),
              ],
            ),
    );
  }
}

class AppMark extends StatelessWidget {
  const AppMark({super.key});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: DecoratedBox(
        decoration: const BoxDecoration(color: Colors.white),
        child: SvgPicture.asset(
          'assets/images/pocket_agenda_logo_minimal.svg',
          width: 52,
          height: 52,
          fit: BoxFit.contain,
        ),
      ),
    );
  }
}

class PageScaffold extends StatelessWidget {
  const PageScaffold({
    required this.title,
    required this.subtitle,
    required this.child,
    super.key,
  });

  final String title;
  final String subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 12),
          sliver: SliverToBoxAdapter(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 980),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const AppMark(),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: Theme.of(context).textTheme.headlineMedium
                              ?.copyWith(fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          subtitle,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          sliver: SliverToBoxAdapter(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 980),
                child: child,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class SmartAddPage extends StatefulWidget {
  const SmartAddPage({super.key});

  @override
  State<SmartAddPage> createState() => _SmartAddPageState();
}

class _SmartAddPageState extends State<SmartAddPage> {
  final controller = TextEditingController(
    text:
        'Dentist appointment on May 20, 2026 at 12:00 PM. Remind me after class.',
  );

  bool showResult = true;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      title: 'Pocket Agenda',
      subtitle: 'A calendar assistant UI prototype with mocked responses.',
      child: LayoutBuilder(
        builder: (context, constraints) {
          final wide = constraints.maxWidth >= 760;
          final input = _SmartInputCard(
            controller: controller,
            onPressed: () => setState(() => showResult = true),
          );
          final preview = showResult
              ? const _EventPreviewCard()
              : const _EmptyPreviewCard();

          if (!wide) {
            return Column(
              children: [input, const SizedBox(height: 12), preview],
            );
          }

          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: input),
              const SizedBox(width: 14),
              Expanded(child: preview),
            ],
          );
        },
      ),
    );
  }
}

class _SmartInputCard extends StatelessWidget {
  const _SmartInputCard({required this.controller, required this.onPressed});

  final TextEditingController controller;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Smart add',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              minLines: 6,
              maxLines: 9,
              decoration: const InputDecoration(
                hintText: 'Describe an event, reminder, or schedule conflict.',
              ),
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: onPressed,
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Preview event'),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.link),
              label: const Text('Backend connection placeholder'),
            ),
          ],
        ),
      ),
    );
  }
}

class _EventPreviewCard extends StatelessWidget {
  const _EventPreviewCard();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.warning_amber, color: Color(0xFFB35C00)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Conflict found',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const EventTile(
              title: 'Dentist appointment',
              time: 'Wed, May 20, 2026 - 12:00 PM to 1:00 PM',
              accent: Color(0xFF0E7C86),
            ),
            const SizedBox(height: 10),
            const EventTile(
              title: 'ENGR213 Lab',
              time: 'Wed, May 20, 2026 - 11:00 AM to 12:15 PM',
              accent: Color(0xFFD95F43),
            ),
            const SizedBox(height: 12),
            Text(
              'Suggested reminder: 12:15 PM, right after class ends.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.event_available),
                    label: const Text('Create'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.edit_calendar),
                    label: const Text('Adjust'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyPreviewCard extends StatelessWidget {
  const _EmptyPreviewCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: SizedBox(
        height: 220,
        child: Center(
          child: Text('Your generated event preview appears here.'),
        ),
      ),
    );
  }
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final controller = TextEditingController();
  final messages = <ChatMessage>[
    const ChatMessage(
      sender: 'Pocket Agenda',
      text: 'Tell me what you need planned, remembered, or reorganized.',
      fromUser: false,
    ),
  ];

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  void sendMessage() {
    final text = controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      messages.add(ChatMessage(sender: 'You', text: text, fromUser: true));
      messages.add(
        const ChatMessage(
          sender: 'Pocket Agenda',
          text:
              'Mock reply: I can turn that into calendar actions once the backend is connected.',
          fromUser: false,
        ),
      );
      controller.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      title: 'AI Chat',
      subtitle: 'Mock conversation view for your Ollama chatbot.',
      child: Card(
        child: SizedBox(
          height: 620,
          child: Column(
            children: [
              Expanded(
                child: ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: messages.length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 10),
                  itemBuilder: (context, index) {
                    return ChatBubble(message: messages[index]);
                  },
                ),
              ),
              const Divider(height: 1),
              Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: controller,
                        decoration: const InputDecoration(
                          hintText: 'Ask about your schedule...',
                        ),
                        onSubmitted: (_) => sendMessage(),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton.filled(
                      onPressed: sendMessage,
                      icon: const Icon(Icons.send),
                      tooltip: 'Send',
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class PlannerPage extends StatelessWidget {
  const PlannerPage({super.key});

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      title: 'Yearly Planner',
      subtitle: 'Simulated months and weeks view before backend integration.',
      child: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(
                        labelText: 'Year goal',
                        hintText: 'Learn Python and prepare for jobs',
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  FilledButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.calendar_view_month),
                    label: const Text('Generate'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          ...mockMonths.map((month) => MonthPlanCard(month: month)),
        ],
      ),
    );
  }
}

class AgendaPage extends StatelessWidget {
  const AgendaPage({super.key});

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      title: 'Agenda',
      subtitle: 'Static calendar list that will come from Google Calendar.',
      child: const Column(
        children: [
          EventTile(
            title: 'ENGR213 Midterm Practice',
            time: 'Tue, May 19, 2026 - 12:00 AM to 1:00 AM',
            accent: Color(0xFF0E7C86),
          ),
          SizedBox(height: 10),
          EventTile(
            title: 'Watch movie',
            time: 'Wed, May 20, 2026 - 10:00 AM to 11:00 AM',
            accent: Color(0xFFD95F43),
          ),
          SizedBox(height: 10),
          EventTile(
            title: 'Python project review',
            time: 'Fri, May 22, 2026 - 3:00 PM to 4:30 PM',
            accent: Color(0xFF3E6C9B),
          ),
        ],
      ),
    );
  }
}

class EventTile extends StatelessWidget {
  const EventTile({
    required this.title,
    required this.time,
    required this.accent,
    super.key,
  });

  final String title;
  final String time;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Container(
              width: 4,
              height: 48,
              decoration: BoxDecoration(
                color: accent,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(time),
                ],
              ),
            ),
            IconButton(
              onPressed: () {},
              icon: const Icon(Icons.open_in_new),
              tooltip: 'Open',
            ),
          ],
        ),
      ),
    );
  }
}

class ChatMessage {
  const ChatMessage({
    required this.sender,
    required this.text,
    required this.fromUser,
  });

  final String sender;
  final String text;
  final bool fromUser;
}

class ChatBubble extends StatelessWidget {
  const ChatBubble({required this.message, super.key});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final color = message.fromUser
        ? Theme.of(context).colorScheme.primary
        : const Color(0xFFE9EEE8);
    final textColor = message.fromUser ? Colors.white : const Color(0xFF182321);

    return Align(
      alignment: message.fromUser
          ? Alignment.centerRight
          : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  message.sender,
                  style: TextStyle(
                    color: textColor.withValues(alpha: 0.76),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(message.text, style: TextStyle(color: textColor)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class MonthPlan {
  const MonthPlan({
    required this.name,
    required this.focus,
    required this.weeks,
  });

  final String name;
  final String focus;
  final List<String> weeks;
}

class MonthPlanCard extends StatelessWidget {
  const MonthPlanCard({required this.month, super.key});

  final MonthPlan month;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        initiallyExpanded: month.name == 'May',
        title: Text(
          month.name,
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        subtitle: Text(month.focus),
        children: [
          for (var index = 0; index < month.weeks.length; index++)
            ListTile(
              leading: CircleAvatar(radius: 15, child: Text('${index + 1}')),
              title: Text('Week ${index + 1}'),
              subtitle: Text(month.weeks[index]),
            ),
        ],
      ),
    );
  }
}

const mockMonths = [
  MonthPlan(
    name: 'May',
    focus: 'Protect appointments and finish coursework.',
    weeks: [
      'Review ENGR213 and confirm all medical appointments.',
      'Block study sessions around labs and commute time.',
      'Prepare job materials and review project notes.',
      'Reflect on schedule conflicts and adjust reminders.',
    ],
  ),
  MonthPlan(
    name: 'June',
    focus: 'Build portfolio momentum.',
    weeks: [
      'Polish Pocket Agenda and write a short README.',
      'Apply to roles and track follow-ups.',
      'Practice interview questions three times.',
      'Plan July goals and clean calendar backlog.',
    ],
  ),
  MonthPlan(
    name: 'July',
    focus: 'Deepen Python and Flutter confidence.',
    weeks: [
      'Connect Flutter to the Python backend.',
      'Add conflict resolution actions.',
      'Test on phone and desktop.',
      'Prepare a demo recording.',
    ],
  ),
];
