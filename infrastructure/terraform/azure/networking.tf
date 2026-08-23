# VNet, subnets, and NSGs for the Container Apps environment and the
# API Management VNet injection. Rule sets below are sourced from Microsoft's
# documented minimums, not guessed:
#   - Container Apps subnet delegation/sizing: learn.microsoft.com/azure/container-apps/custom-virtual-networks
#   - APIM external-VNet NSG rules:            learn.microsoft.com/azure/api-management/api-management-using-with-vnet
# Both were verified current as of this module's authoring; re-check before
# relying on this for production, since Azure's required rule sets do change.

resource "azurerm_virtual_network" "main" {
  name                = "vnet-${local.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = ["10.10.0.0/16"]
  tags                = var.tags
}

# --- Container Apps environment subnet --------------------------------------
# Workload-profile environments (the current default) require a /27 minimum
# and MUST delegate the subnet to Microsoft.App/environments.

resource "azurerm_subnet" "container_apps" {
  name                 = "snet-container-apps"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.10.0.0/27"]

  delegation {
    name = "container-apps-delegation"

    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_network_security_group" "container_apps" {
  name                = "nsg-container-apps-${local.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags

  # External ingress to the environment's managed load balancer arrives via
  # its public IP, not through this subnet, but the platform still needs to
  # reach the nodes inside it -- default Azure intra-VNet rules cover that.
  # This rule set only needs to stop unsolicited inbound from outside Azure.
  security_rule {
    name                       = "DenyInternetInbound"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "container_apps" {
  subnet_id                 = azurerm_subnet.container_apps.id
  network_security_group_id = azurerm_network_security_group.container_apps.id
}

# --- API Management subnet ---------------------------------------------------
# External VNet mode. Per Microsoft's docs this subnet must NOT have a
# delegation configured (Delegate subnet to a service = None).

resource "azurerm_subnet" "apim" {
  name                 = "snet-apim"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.10.0.32/27"]
}

resource "azurerm_network_security_group" "apim" {
  name                = "nsg-apim-${local.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags

  # Inbound: client traffic to the gateway/developer portal.
  security_rule {
    name                       = "AllowClientCommunicationInbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["80", "443"]
    source_address_prefix      = "Internet"
    destination_address_prefix = "VirtualNetwork"
  }

  # Inbound: management plane (Azure portal / PowerShell / CLI / REST).
  security_rule {
    name                       = "AllowApiManagementEndpointInbound"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3443"
    source_address_prefix      = "ApiManagement"
    destination_address_prefix = "VirtualNetwork"
  }

  # Inbound: Azure's infrastructure load balancer (stv2 platform).
  security_rule {
    name                       = "AllowAzureLoadBalancerInbound"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "6390"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "VirtualNetwork"
  }

  # Outbound: certificate validation/management.
  security_rule {
    name                       = "AllowCertificateManagementOutbound"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "Internet"
  }

  # Outbound: core dependency on Azure Storage.
  security_rule {
    name                       = "AllowStorageOutbound"
    priority                   = 110
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "Storage"
  }

  # Outbound: core dependency on Azure SQL.
  security_rule {
    name                       = "AllowSqlOutbound"
    priority                   = 120
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "1433"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "SQL"
  }

  # Outbound: core dependency on Azure Key Vault.
  security_rule {
    name                       = "AllowKeyVaultOutbound"
    priority                   = 130
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "AzureKeyVault"
  }

  # Outbound: publish diagnostics, metrics, and Application Insights data.
  security_rule {
    name                       = "AllowAzureMonitorOutbound"
    priority                   = 140
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["443", "1886"]
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "AzureMonitor"
  }
}

resource "azurerm_subnet_network_security_group_association" "apim" {
  subnet_id                 = azurerm_subnet.apim.id
  network_security_group_id = azurerm_network_security_group.apim.id
}
