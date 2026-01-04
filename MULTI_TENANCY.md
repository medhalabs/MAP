# Multi-Tenancy Implementation

MedhaAlgoPilot now supports multi-tenancy, allowing organizations to manage multiple users, strategies, and broker accounts with complete data isolation.

## Architecture

### Database Schema

1. **Tenant Model** - Represents an organization/tenant
   - `id` - Primary key
   - `name` - Organization name
   - `slug` - URL-friendly identifier
   - `domain` - Optional custom domain
   - `subscription_tier` - free, pro, enterprise
   - `max_users` - Maximum users allowed
   - `max_strategies` - Maximum strategies allowed

2. **User Model** - Updated with tenant relationship
   - `tenant_id` - Foreign key to tenants
   - `is_tenant_admin` - Admin within tenant
   - Email/username uniqueness is scoped to tenant

3. **All Resource Models** - Tenant-scoped
   - `Strategy` - Has `tenant_id`
   - `BrokerAccount` - Has `tenant_id`
   - All queries filter by `tenant_id`

## Features

### Tenant Isolation

- All data is isolated per tenant
- Users can only access data within their tenant
- API routes automatically filter by tenant
- Cross-tenant access is prevented

### Tenant Administration

- First user in tenant becomes admin (`is_tenant_admin = true`)
- Admins can view all users in their tenant
- Admins can manage tenant settings

### Registration Flow

1. **New Tenant**: User registers without tenant → Creates new tenant
2. **Join Tenant**: User provides `tenant_slug` → Joins existing tenant
3. **Specify Tenant**: User provides `tenant_id` → Joins specific tenant

## API Changes

### Authentication

- JWT tokens include user ID (tenant is derived from user)
- All authenticated endpoints automatically filter by tenant

### New Endpoints

- `GET /api/tenants/current` - Get current tenant info
- `GET /api/tenants/users` - List users in tenant (admin only)

### Updated Endpoints

All resource endpoints now filter by tenant:
- Strategies: `GET /api/strategies` - Returns tenant's strategies
- Orders: `GET /api/orders` - Returns tenant's orders
- Trades: `GET /api/trades` - Returns tenant's trades
- Positions: `GET /api/positions` - Returns tenant's positions

## Usage

### Registration

```json
POST /api/auth/register
{
  "email": "user@example.com",
  "username": "user",
  "password": "password",
  "tenant_slug": "my-org"  // Optional: join existing tenant
}
```

### Accessing Tenant Info

```typescript
// Frontend
const tenant = await apiClient.get('/api/tenants/current')
```

## Security

- Tenant isolation enforced at database level
- API routes use `get_current_tenant` dependency
- Cross-tenant queries are prevented
- Tenant admins can only manage their own tenant

## Migration

Existing installations need to:

1. Add `tenant_id` to all tables
2. Create default tenant for existing users
3. Migrate existing data to tenant

See migration scripts in `backend/alembic/versions/` (to be created).

