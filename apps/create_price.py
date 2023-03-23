import stripe
stripe.api_key = "sk_test_51MolceSCy9vRZRqu8jDVMA76vGEI4aOV3p6XPQKTL0TJAv5eWSeqsHBB8GgVhKNwawukzBHKekYCnSQ2Ai6cIE5I00A8iB6eNe"

starter_subscription = stripe.Product.create(
  name="Starter Subscription",
  description="$12/Month subscription",
)

starter_subscription_price = stripe.Price.create(
  unit_amount=1200,
  currency="inr",
  recurring={"interval": "month"},
  product=starter_subscription['id'],
)

# Save these identifiers
print(f"Success! Here is your starter subscription product id: {starter_subscription.id}")
print(f"Success! Here is your starter subscription price id: {starter_subscription_price.id}")