from rules import evaluate_validation_rules, summarize_rule_results

cases = {
    "empty": "",
    "good": (
        "Document Title\n"
        "v1.0\n"
        "Revision History\n"
        "2024-01-01: initial\n"
        "Signature: Approved by Alice\n"
    ),
    "partial": (
        "\n"  # empty first line -> no title
        "This document contains lorem ipsum and teh mistakes.\n"
        "No version here.\n"
        "Signature: none\n"
    )
}

for name, text in cases.items():
    if name == 'good':
        res = evaluate_validation_rules(text, document_title='Document Title', version='v1.0', metadata={'has_audit_trail': True}, file_name='doc.pdf')
    else:
        res = evaluate_validation_rules(text, document_title='', version='', metadata={})
    summary = summarize_rule_results(res)
    print(f"--- CASE: {name} ---")
    print("Summary:", summary)
    for r in res:
        print(f"{r['id']}: {r['title']} -> {r['status']} | {r['evidence']}")
    print()
