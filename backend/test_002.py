from app.services.ml_analyzer import ml_analyzer
from app.services.rule_engine import rule_engine

body="""Dear Customer,\n\nYour purchase of the 'Pro Video Editor Suite' (1-Year Subscription) for $199.99 was successful. This amount will be billed to your card on file.\n\nIf you did not authorize this purchase or wish to cancel your subscription, please visit the resolution center immediately to process a refund: https://www.аpple.com/support/refund\n\nThank you,\nBilling Support"""
subject="Receipt"

print("ML...")
r1 = ml_analyzer.analyze_text(subject, body)
print(r1)
print("Rules...")
r2 = rule_engine.check_credentials(body)
print(r2)
print("Done")
