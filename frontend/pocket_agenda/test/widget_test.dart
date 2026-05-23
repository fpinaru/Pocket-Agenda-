import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:pocket_agenda/main.dart';

void main() {
  testWidgets('Pocket Agenda shell renders main actions', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const PocketAgendaApp());

    expect(find.text('Pocket Agenda'), findsOneWidget);
    expect(find.text('Smart add'), findsOneWidget);
    expect(find.text('Preview event'), findsOneWidget);
  });

  testWidgets('Chat tab accepts a mock message', (WidgetTester tester) async {
    await tester.pumpWidget(const PocketAgendaApp());

    await tester.tap(find.text('Chat').last);
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byType(EditableText).last,
      'Help me plan tomorrow',
    );
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pump();

    expect(find.text('Help me plan tomorrow'), findsOneWidget);
  });
}
