GASTOS_FIJOS = [
    "Rent", "Personal Care", "Groceries", "Utilities", "Subscriptions", 
    "Transport", "Insurance", "Healthcare", "Other", "Pharmacy ", 
    "Maintenance ", "Tax", "Acommodation"
]

SECUNDARIOS = ["Sport", "Education", "Travel"]

CHAO_CULPA = [
    "Coffee-Snacks", "Restaurant", "Alcohol", "Activities", 
    "Shopping", "Snacks & Coffee", "Gifts"
]

PASIVOS = ["Mortgage", "Rental Apartment", "Investments", "Savings"]

# Build the BUDGETS dictionary from the categorical lists
BUDGETS = {}
for cat in GASTOS_FIJOS: BUDGETS[cat] = "Gastos fijos"
for cat in SECUNDARIOS: BUDGETS[cat] = "Secundarios"
for cat in CHAO_CULPA: BUDGETS[cat] = "Chao culpa"
for cat in PASIVOS: BUDGETS[cat] = "Pasivos"

SORT_ORDER = {
    "Gastos fijos": 1,
    "Secundarios": 2,
    "Chao culpa": 3,
    "Pasivos": 4
}

