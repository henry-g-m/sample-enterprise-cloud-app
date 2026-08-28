# Cost Management budget on the resource group. Monthly grain auto-recurs
# from start_date, so that date only needs to be set once at first apply --
# it is deliberately a literal rather than timestamp()/formatdate(), since a
# volatile value here would cause Terraform to see drift on every plan.
resource "azurerm_consumption_budget_resource_group" "main" {
  name              = "budget-${var.project_name}-${var.environment}"
  resource_group_id = azurerm_resource_group.main.id

  amount     = var.budget_amount
  time_grain = "Monthly"

  time_period {
    start_date = "2026-08-01T00:00:00Z"
  }

  notification {
    enabled        = true
    threshold      = 20
    operator       = "GreaterThanOrEqualTo"
    contact_emails = var.budget_alert_emails
  }

  notification {
    enabled        = true
    threshold      = 50
    operator       = "GreaterThanOrEqualTo"
    contact_emails = var.budget_alert_emails
  }

  notification {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    contact_emails = var.budget_alert_emails
  }
}
