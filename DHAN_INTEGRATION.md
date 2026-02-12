# Dhan API v2 Integration Guide

This document describes the DhanHQ API v2 integration for MedhaAlgoPilot.

## Overview

MedhaAlgoPilot integrates with [DhanHQ API v2](https://dhanhq.co/docs/v2/) to provide seamless algorithmic trading capabilities.

### Dhan API v2 Features

- **REST-like APIs** - Standard HTTP methods with JSON/form-encoded requests
- **High Performance**:
  - 25 orders/sec
  - < 100 ms API response latency
  - 7000 orders/day limit
- **Advanced Features**:
  - Bulk order placement with order slicing
  - Advanced order types (Market, Limit, Stop Loss, etc.)
  - Margin Trading Facility (MTF) - up to 4X margin on 950+ stocks
  - Real-time market feed data
- **Developer-Friendly**:
  - Sandbox environment for testing
  - Comprehensive API documentation
  - Official Python SDK available

## API v2 Key Changes

### Base URLs
- **Production**: `https://api.dhan.co/v2`
- **Sandbox**: `https://api-sandbox.dhan.co/v2`

### Request Format
- **GET/DELETE**: Query parameters
- **POST/PUT**: Form-encoded data (not JSON)

### Authentication
- Only `access-token` header required (JWT token)
- Access tokens valid for 24 hours
- No `X-API-KEY` header needed

### Error Structure
```json
{
    "errorType": "ErrorType",
    "errorCode": "ERROR_CODE",
    "errorMessage": "Error message description"
}
```

### Parameter Names
- Uses `clientId` instead of `dhanClientId`
- Uses `securityId` instead of `symbol` for orders (requires instrument lookup)

## Getting Started

### Step 1: Create Dhan Account

1. Visit [DhanHQ Developer Portal](https://dhan.co/developer)
2. Create a developer account
3. Get your API credentials:
   - **Client ID** (API Key)
   - **Access Token** (JWT, valid for 24 hours, obtained via OAuth)
   - **Account ID** (Your Dhan Client ID)

### Step 2: Generate Access Token

Access tokens in v2 are valid for 24 hours. You need to:
1. Authenticate via OAuth flow
2. Obtain JWT access token
3. Refresh token before expiry

**Note**: For production, implement token refresh logic to automatically renew tokens.

### Step 3: Add Broker Account in MedhaAlgoPilot

1. Go to **Settings** → **Broker Accounts**
2. Click **Add Broker Account**
3. Fill in the details:
   - **Broker**: Dhan
   - **Account ID**: Your Dhan Client ID
   - **API Key**: Your Dhan Client ID (same as Account ID)
   - **Access Token**: Your Dhan Access Token (JWT)
   - **Set as default**: Check if this is your primary account

### Step 4: Test Connection

The system will automatically test the connection when you:
- Add a broker account (validates credentials)
- Start a strategy run
- Place your first order

## API Endpoints Used

### Order Management

- **Place Order**: `POST /v2/orders` (form-encoded)
- **Cancel Order**: `DELETE /v2/orders/{orderId}` (query params)
- **Modify Order**: `PUT /v2/orders/{orderId}` (form-encoded)
- **Get Order Status**: `GET /v2/orders/{orderId}` (query params)
- **Fetch Orders**: `GET /v2/orders` (query params)

### Portfolio & Positions

- **Get Positions**: `GET /v2/portfolio/positions` (query params)
- **Get Holdings**: `GET /v2/portfolio/holdings` (query params)

### Funds

- **Get Funds**: `GET /v2/funds` (query params)

### Market Data

- **Market Quote**: `GET /v2/market-quote` (query params)
- **Historical Data**: `GET /v2/historical-data` (query params)
- **Option Chain**: `GET /v2/option-chain` (query params)

## Order Types Supported

1. **MARKET** - Market orders (executed immediately at market price)
2. **LIMIT** - Limit orders (executed at specified price or better)
3. **SL** - Stop Loss Market orders
4. **SL-M** - Stop Loss Limit orders

## Product Types Supported

1. **INTRADAY** - Intraday trading
2. **MARGIN** - Margin trading (MTF)
3. **CASH** - Cash segment
4. **CNC** - Cash and Carry
5. **CO** - Cover Order
6. **BO** - Bracket Order

## Exchange Segments

- **NSE_EQ** - NSE Equity
- **BSE_EQ** - BSE Equity
- **NSE_FO** - NSE Futures & Options
- **BSE_FO** - BSE Futures & Options
- **MCX_COMM** - MCX Commodities

## Sandbox vs Live Trading

### Sandbox Mode (Paper Trading)

- Use sandbox environment for testing
- No real money involved
- Test strategies safely
- Sandbox URL: `https://api-sandbox.dhan.co/v2`

### Live Trading

- Real money trading
- Production environment
- Requires verified Dhan account
- Production URL: `https://api.dhan.co/v2`

## Rate Limits (v2)

| API Type | Per Second | Per Minute | Per Hour | Per Day |
|----------|------------|------------|----------|---------|
| Order APIs | 25 | 250 | 1000 | 7000 |
| Data APIs | 5 | - | - | 100000 |
| Quote APIs | 1 | Unlimited | Unlimited | Unlimited |
| Non-Trading APIs | 20 | Unlimited | Unlimited | Unlimited |

**Note**: Order modifications are capped at 25 modifications per order.

## Error Handling

The Dhan adapter handles various error scenarios:

- **Network Errors**: Retries and graceful degradation
- **API Errors**: Detailed error messages from Dhan API v2 format
- **Authentication Errors**: Clear messages for invalid/expired tokens
- **Rate Limiting**: Respects rate limits with proper error handling

### Error Response Format

```json
{
    "errorType": "ValidationError",
    "errorCode": "INVALID_PARAMETER",
    "errorMessage": "Invalid securityId provided"
}
```

## Important Notes

### Security ID Requirement

The v2 API uses `securityId` instead of `symbol` for placing orders. You need to:
1. Fetch the instrument list from Dhan
2. Map symbol to securityId
3. Use securityId when placing orders

**Current Implementation**: The adapter uses symbol as-is for now. For production, implement proper securityId lookup.

### Access Token Management

- Access tokens expire after 24 hours
- Implement token refresh logic for production
- Store tokens securely (encrypted in database)
- Handle token expiry gracefully

### Static IP Requirement

For production trading, Dhan requires a static IP address. You can:
1. Set up static IP via Dhan API
2. Configure your server with static IP
3. Whitelist IP in Dhan portal

## Best Practices

1. **Start with Sandbox**: Always test in sandbox mode first
2. **Handle Errors**: Implement proper error handling in strategies
3. **Respect Rate Limits**: Don't exceed 25 orders/sec
4. **Monitor Orders**: Check order status regularly
5. **Use Limit Orders**: For better price control
6. **Test Connection**: Verify broker account before live trading
7. **Token Refresh**: Implement automatic token refresh for production
8. **Security ID Mapping**: Maintain symbol to securityId mapping

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify Access Token is valid and not expired
   - Check if token was generated within last 24 hours
   - Regenerate access token if needed
   - Verify Client ID is correct

2. **Order Rejected**
   - Check order parameters (securityId, quantity, price)
   - Verify sufficient margin/balance
   - Check if market is open
   - Ensure securityId is correct (not symbol)

3. **Connection Timeout**
   - Check internet connection
   - Verify Dhan API status
   - Retry the operation
   - Check firewall settings

4. **Rate Limit Exceeded**
   - Reduce order frequency
   - Implement backoff strategy
   - Batch orders when possible
   - Monitor rate limit usage

5. **Invalid Security ID**
   - Fetch instrument list from Dhan
   - Map symbol to securityId correctly
   - Use securityId in order requests

## API Documentation

For detailed API documentation, visit:
- [DhanHQ API v2 Documentation](https://dhanhq.co/docs/v2/)
- [DhanHQ Python SDK](https://dhanhq.co/docs/DhanHQ-py/)
- [Developer Portal](https://dhan.co/developer)
- [Release Notes](https://dhanhq.co/docs/v2/releases/)

## Support

For Dhan API support:
- Email: apihelp@dhan.co
- Developer Portal: https://dhan.co/developer
- Documentation: https://dhanhq.co/docs/v2/

## Security Notes

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Rotate access tokens** regularly (every 24 hours)
- **Use sandbox** for development and testing
- **Enable 2FA** on your Dhan account
- **Encrypt tokens** in database
- **Use HTTPS** for all API calls

## Integration Status

✅ **Implemented Features**:
- Place order (v2 API)
- Cancel order (v2 API)
- Modify order (v2 API)
- Get order status (v2 API)
- Fetch orders (v2 API)
- Fetch positions (v2 API)
- Get holdings (v2 API)
- Get account balance (v2 API)
- Market quote (v2 API)
- Error handling (v2 format)
- Connection testing

🔄 **Future Enhancements**:
- Real-time market data streaming
- WebSocket integration
- Bulk order placement
- Advanced order types (CO, BO)
- Historical data API
- Instrument list caching
- Security ID mapping
- Automatic token refresh
- Static IP configuration

## Migration from v1 to v2

If you're migrating from v1 API:

1. **Update Base URL**: Change to `/v2` endpoints
2. **Update Request Format**: Use form-encoded for POST/PUT
3. **Update Headers**: Remove X-API-KEY, keep only access-token
4. **Update Parameter Names**: Use `clientId` instead of `dhanClientId`
5. **Update Error Handling**: Handle new error structure
6. **Implement Security ID**: Map symbols to securityIds
7. **Token Management**: Implement 24-hour token refresh
